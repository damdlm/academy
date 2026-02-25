import json
from app import create_app
from models import db, Treino, Musculo, Exercicio, VersaoGlobal, TreinoVersao, VersaoExercicio, RegistroTreino, HistoricoTreino
from datetime import datetime
from pathlib import Path

def migrar_dados():
    app = create_app()
    with app.app_context():
        print("🚀 Iniciando migração de dados...")
        
        # Limpar dados existentes
        db.session.query(HistoricoTreino).delete()
        db.session.query(RegistroTreino).delete()
        db.session.query(VersaoExercicio).delete()
        db.session.query(TreinoVersao).delete()
        db.session.query(VersaoGlobal).delete()
        db.session.query(Exercicio).delete()
        db.session.query(Musculo).delete()
        db.session.query(Treino).delete()
        db.session.commit()
        
        # =========================================
        # 1. Migrar treinos.json
        # =========================================
        print("📥 Migrando treinos...")
        with open('storage/treinos.json', 'r', encoding='utf-8') as f:
            treinos_data = json.load(f)
        
        for t in treinos_data:
            treino = Treino(id=t['id'], descricao=t['descricao'])
            db.session.add(treino)
        db.session.commit()
        print(f"✅ {len(treinos_data)} treinos migrados")
        
        # =========================================
        # 2. Migrar musculos.json
        # =========================================
        print("📥 Migrando músculos...")
        with open('storage/musculos.json', 'r', encoding='utf-8') as f:
            musculos_data = json.load(f)
        
        musculo_map = {}  # Para mapear nome -> id
        for m in musculos_data:
            musculo = Musculo(nome=m.lower(), nome_exibicao=m)
            db.session.add(musculo)
            db.session.flush()
            musculo_map[m] = musculo.id
        db.session.commit()
        print(f"✅ {len(musculos_data)} músculos migrados")
        
        # =========================================
        # 3. Migrar exercicios.json
        # =========================================
        print("📥 Migrando exercícios...")
        with open('storage/exercicios.json', 'r', encoding='utf-8') as f:
            exercicios_data = json.load(f)
        
        for ex in exercicios_data:
            musculo_id = musculo_map.get(ex['musculo'])
            exercicio = Exercicio(
                id=ex['id'],
                nome=ex['nome'],
                musculo_id=musculo_id,
                treino_id=ex.get('treino')
            )
            db.session.add(exercicio)
        db.session.commit()
        print(f"✅ {len(exercicios_data)} exercícios migrados")
        
        # =========================================
        # 4. Migrar versoes_treino.json
        # =========================================
        print("📥 Migrando versões...")
        with open('storage/versoes_treino.json', 'r', encoding='utf-8') as f:
            versoes_data = json.load(f)
        
        versao_map = {}  # id_antigo -> id_novo
        for v in versoes_data:
            versao = VersaoGlobal(
                numero_versao=v['versao'],
                descricao=v['descricao'],
                data_inicio=datetime.strptime(v['data_inicio'], '%Y-%m-%d').date(),
                data_fim=datetime.strptime(v['data_fim'], '%Y-%m-%d').date() if v.get('data_fim') else None
            )
            db.session.add(versao)
            db.session.flush()
            versao_map[v['id']] = versao.id
            
            # Migrar treinos da versão
            if 'treinos' in v:
                for treino_id, treino_data in v['treinos'].items():
                    if isinstance(treino_data, dict):
                        # Novo formato
                        treino_versao = TreinoVersao(
                            versao_id=versao.id,
                            treino_id=treino_id,
                            nome_treino=treino_data.get('nome', f'Treino {treino_id}'),
                            descricao_treino=treino_data.get('descricao', '')
                        )
                    else:
                        # Formato antigo (lista de exercícios)
                        treino_versao = TreinoVersao(
                            versao_id=versao.id,
                            treino_id=treino_id,
                            nome_treino=f'Treino {treino_id}',
                            descricao_treino=''
                        )
                    db.session.add(treino_versao)
                    db.session.flush()
                    
                    # Adicionar exercícios ao treino da versão
                    exercicios_lista = treino_data if isinstance(treino_data, list) else treino_data.get('exercicios', [])
                    for ordem, ex_id in enumerate(exercicios_lista):
                        versao_ex = VersaoExercicio(
                            treino_versao_id=treino_versao.id,
                            exercicio_id=ex_id,
                            ordem=ordem
                        )
                        db.session.add(versao_ex)
        
        db.session.commit()
        print(f"✅ {len(versoes_data)} versões migradas")
        
        # =========================================
        # 5. Migrar registros.json
        # =========================================
        print("📥 Migrando registros...")
        with open('storage/registros.json', 'r', encoding='utf-8') as f:
            registros_data = json.load(f)
        
        for r in registros_data:
            versao_id = versao_map.get(r.get('versao_global_id'))
            
            registro = RegistroTreino(
                treino_id=r['treino'],
                versao_id=versao_id,
                periodo=r['periodo'],
                semana=r['semana'],
                exercicio_id=r['exercicio_id'],
                data_registro=datetime.fromisoformat(r['data_registro']) if 'data_registro' in r else datetime.now()
            )
            db.session.add(registro)
            db.session.flush()
            
            # Migrar séries
            series = r.get('series', [])
            if not series and 'carga' in r and 'repeticoes' in r:
                # Formato antigo
                series = [{'carga': r['carga'], 'repeticoes': r['repeticoes']}]
            
            for ordem, s in enumerate(series):
                serie = HistoricoTreino(
                    registro_id=registro.id,
                    carga=s['carga'],
                    repeticoes=s['repeticoes'],
                    ordem=ordem
                )
                db.session.add(serie)
        
        db.session.commit()
        print(f"✅ {len(registros_data)} registros migrados")
        
        print("🎉 Migração concluída com sucesso!")

if __name__ == "__main__":
    migrar_dados()