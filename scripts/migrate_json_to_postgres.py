#!/usr/bin/env python3
"""
Script para migrar dados dos arquivos JSON para o PostgreSQL
Execute apenas uma vez após configurar o banco de dados
"""

import json
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from models import db, Treino, Musculo, Exercicio, VersaoGlobal, TreinoVersao, VersaoExercicio, RegistroTreino, HistoricoTreino
from datetime import datetime
from flask_login import current_user

def migrar_dados():
    """Executa a migração dos dados"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🚀 Iniciando migração de dados...")
        print("=" * 60)
        
        # Verificar se já existem dados
        if Treino.query.count() > 0:
            resposta = input("⚠️  Já existem dados no banco. Deseja limpar e migrar novamente? (s/N): ")
            if resposta.lower() != 's':
                print("❌ Migração cancelada")
                return
            
            # Limpar dados existentes
            print("🗑️  Limpando dados existentes...")
            HistoricoTreino.query.delete()
            RegistroTreino.query.delete()
            VersaoExercicio.query.delete()
            TreinoVersao.query.delete()
            VersaoGlobal.query.delete()
            Exercicio.query.delete()
            Musculo.query.delete()
            Treino.query.delete()
            db.session.commit()
            print("✅ Dados antigos removidos")
        
        # =========================================
        # 1. Migrar treinos.json
        # =========================================
        print("\n📥 Migrando treinos...")
        treinos_path = Path('storage/treinos.json')
        if treinos_path.exists():
            with open(treinos_path, 'r', encoding='utf-8') as f:
                treinos_data = json.load(f)
            
            # Usar usuário admin (ID 1)
            admin_id = 1
            
            for t in treinos_data:
                treino = Treino(
                    codigo=t['id'],
                    nome=f"Treino {t['id']}",
                    descricao=t['descricao'],
                    user_id=admin_id
                )
                db.session.add(treino)
            db.session.commit()
            print(f"✅ {len(treinos_data)} treinos migrados")
        else:
            print("⚠️  Arquivo treinos.json não encontrado")
        
        # =========================================
        # 2. Migrar musculos.json
        # =========================================
        print("\n📥 Migrando músculos...")
        musculos_path = Path('storage/musculos.json')
        if musculos_path.exists():
            with open(musculos_path, 'r', encoding='utf-8') as f:
                musculos_data = json.load(f)
            
            musculo_map = {}
            for m in musculos_data:
                musculo = Musculo(
                    nome=m.lower(),
                    nome_exibicao=m
                )
                db.session.add(musculo)
                db.session.flush()
                musculo_map[m] = musculo.id
            db.session.commit()
            print(f"✅ {len(musculos_data)} músculos migrados")
        else:
            print("⚠️  Arquivo musculos.json não encontrado")
            musculo_map = {}
        
        # =========================================
        # 3. Migrar exercicios.json
        # =========================================
        print("\n📥 Migrando exercícios...")
        exercicios_path = Path('storage/exercicios.json')
        if exercicios_path.exists():
            with open(exercicios_path, 'r', encoding='utf-8') as f:
                exercicios_data = json.load(f)
            
            for ex in exercicios_data:
                musculo_id = musculo_map.get(ex['musculo'])
                exercicio = Exercicio(
                    nome=ex['nome'],
                    musculo_id=musculo_id,
                    treino_id=ex.get('treino'),
                    user_id=admin_id
                )
                db.session.add(exercicio)
            db.session.commit()
            print(f"✅ {len(exercicios_data)} exercícios migrados")
        else:
            print("⚠️  Arquivo exercicios.json não encontrado")
        
        # =========================================
        # 4. Migrar versoes_treino.json
        # =========================================
        print("\n📥 Migrando versões...")
        versoes_path = Path('storage/versoes_treino.json')
        if versoes_path.exists():
            with open(versoes_path, 'r', encoding='utf-8') as f:
                versoes_data = json.load(f)
            
            versao_map = {}
            for v in versoes_data:
                versao = VersaoGlobal(
                    numero_versao=v['versao'],
                    descricao=v['descricao'],
                    data_inicio=datetime.strptime(v['data_inicio'], '%Y-%m-%d').date(),
                    data_fim=datetime.strptime(v['data_fim'], '%Y-%m-%d').date() if v.get('data_fim') else None,
                    user_id=admin_id
                )
                db.session.add(versao)
                db.session.flush()
                versao_map[v['id']] = versao.id
                
                # Migrar treinos da versão
                if 'treinos' in v:
                    for treino_id, treino_data in v['treinos'].items():
                        if isinstance(treino_data, dict):
                            treino_versao = TreinoVersao(
                                versao_id=versao.id,
                                treino_id=treino_id,
                                nome_treino=treino_data.get('nome', f'Treino {treino_id}'),
                                descricao_treino=treino_data.get('descricao', '')
                            )
                        else:
                            treino_versao = TreinoVersao(
                                versao_id=versao.id,
                                treino_id=treino_id,
                                nome_treino=f'Treino {treino_id}',
                                descricao_treino=''
                            )
                        db.session.add(treino_versao)
                        db.session.flush()
                        
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
        else:
            print("⚠️  Arquivo versoes_treino.json não encontrado")
        
        # =========================================
        # 5. Migrar registros.json
        # =========================================
        print("\n📥 Migrando registros...")
        registros_path = Path('storage/registros.json')
        if registros_path.exists():
            with open(registros_path, 'r', encoding='utf-8') as f:
                registros_data = json.load(f)
            
            for r in registros_data:
                versao_id = versao_map.get(r.get('versao_global_id'))
                
                registro = RegistroTreino(
                    treino_id=r['treino'],
                    versao_id=versao_id,
                    periodo=r['periodo'],
                    semana=r['semana'],
                    exercicio_id=r['exercicio_id'],
                    data_registro=datetime.fromisoformat(r['data_registro']) if 'data_registro' in r else datetime.now(),
                    user_id=admin_id
                )
                db.session.add(registro)
                db.session.flush()
                
                series = r.get('series', [])
                if not series and 'carga' in r and 'repeticoes' in r:
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
        else:
            print("⚠️  Arquivo registros.json não encontrado")
        
        print("\n" + "=" * 60)
        print("🎉 Migração concluída com sucesso!")
        print("=" * 60)

if __name__ == "__main__":
    migrar_dados()