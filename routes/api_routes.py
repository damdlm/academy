from flask import Blueprint, jsonify, request
import json
import unicodedata
from utils import (
    load_json, buscar_musculo_no_catalogo,
    get_series_from_registro, calcular_media_series, calcular_volume_total,
    get_exercicios_do_treino, verificar_exercicio_em_versoes, save_json
)

api_bp = Blueprint('api', __name__)

def remover_acentos(texto):
    """Remove acentos de uma string"""
    if not texto:
        return texto
    texto = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in texto if not unicodedata.combining(c)])

@api_bp.route("/api/progresso")
def api_progresso():
    registros = load_json("registros.json")
    treino = request.args.get("treino")
    
    ordem_meses = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    
    semanas = {}
    for r in registros:
        if treino and r["treino"] != treino:
            continue
            
        key = f"{r['periodo']}_{r['semana']}"
        
        periodo_parts = r["periodo"].split('/')
        mes = periodo_parts[0].strip()
        ano = int(periodo_parts[1]) if len(periodo_parts) > 1 else 2024
        
        if key not in semanas:
            semanas[key] = {
                "periodo": r["periodo"],
                "semana": r["semana"],
                "volume_total": 0,
                "carga_media": 0,
                "qtd_exercicios": 0,
                "ano": ano,
                "mes_num": ordem_meses.get(mes, 0),
                "mes_nome": mes
            }
        
        series = get_series_from_registro(r)
        volume_exercicio = calcular_volume_total(series)
        semanas[key]["volume_total"] += volume_exercicio
        semanas[key]["qtd_exercicios"] += 1
    
    for key in semanas:
        if semanas[key]["qtd_exercicios"] > 0:
            semanas[key]["carga_media"] = round(semanas[key]["volume_total"] / semanas[key]["qtd_exercicios"], 1)
    
    semanas_ordenadas = sorted(
        semanas.values(),
        key=lambda x: (x["ano"], x["mes_num"], x["semana"])
    )
    
    return jsonify({
        "semanas": [f"{s['periodo']} - S{s['semana']}" for s in semanas_ordenadas],
        "volumes": [s["volume_total"] for s in semanas_ordenadas],
        "cargas_medias": [s["carga_media"] for s in semanas_ordenadas]
    })

@api_bp.route("/api/buscar-musculo")
def api_buscar_musculo():
    nome = request.args.get("nome", "").strip()
    
    if not nome:
        return jsonify({"encontrado": False, "mensagem": "Nome do exercício não fornecido"})
    
    musculo = buscar_musculo_no_catalogo(nome)
    
    if musculo:
        return jsonify({
            "encontrado": True, 
            "musculo": musculo,
            "mensagem": f"Músculo encontrado: {musculo}"
        })
    else:
        return jsonify({
            "encontrado": False, 
            "mensagem": "Músculo não encontrado no catálogo"
        })

@api_bp.route("/api/buscar-exercicios")
def api_buscar_exercicios():
    termo = request.args.get("termo", "").strip()
    from app import BASE
    catalogo_path = BASE / "exercises-ptbr-full-translation.json"
    
    # Normalizar o termo de busca (remover acentos)
    termo_normalizado = remover_acentos(termo.lower())
    
    print(f"🔍 API Busca - Termo original: '{termo}'")
    print(f"🔍 API Busca - Termo normalizado: '{termo_normalizado}'")
    
    if not catalogo_path.exists():
        print(f"❌ Arquivo não encontrado: {catalogo_path}")
        # Tenta listar arquivos na pasta storage
        try:
            arquivos = list(BASE.glob("*.json"))
            print(f"📋 Arquivos encontrados: {[f.name for f in arquivos]}")
        except Exception as e:
            print(f"Erro ao listar: {e}")
        return jsonify([])
    
    try:
        with open(catalogo_path, 'r', encoding='utf-8') as f:
            catalogo = json.load(f)
        
        print(f"✅ Catálogo carregado com {len(catalogo)} exercícios")
        
        resultados = []
        
        # Mapeamento de músculos (para exibição)
        mapa_musculos = {
            'abdominais': 'Abdômen',
            'abductors': 'Abdutores',
            'adductors': 'Adutores',
            'biceps': 'Bíceps',
            'calves': 'Panturrilhas',
            'chest': 'Peitoral',
            'forearms': 'Antebraços',
            'glutes': 'Glúteos',
            'hamstrings': 'Posterior de Coxa',
            'lats': 'Dorsal',
            'lower back': 'Lombar',
            'middle back': 'Costas',
            'neck': 'Pescoço',
            'quadriceps': 'Quadríceps',
            'shoulders': 'Ombros',
            'traps': 'Trapézio',
            'triceps': 'Tríceps'
        }
        
        for ex in catalogo:
            nome = ex.get('name', '')
            primary_muscles = ex.get('primaryMuscles', [])
            musculo_original = primary_muscles[0] if primary_muscles else "Não especificado"
            
            # Normalizar o nome do exercício para busca
            nome_normalizado = remover_acentos(nome.lower())
            
            # Converter músculo para português para exibição
            musculo_exibicao = mapa_musculos.get(musculo_original.lower(), musculo_original.title())
            
            if termo:
                # Busca no nome normalizado (sem acentos)
                if termo_normalizado in nome_normalizado:
                    # Gerar um ID único baseado no nome
                    import hashlib
                    id_hash = int(hashlib.md5(nome.encode()).hexdigest()[:8], 16)
                    
                    resultados.append({
                        "id": id_hash,
                        "nome": nome,
                        "musculo": musculo_exibicao
                    })
            else:
                # Se não tem termo, retorna os primeiros 200
                if len(resultados) < 200:
                    import hashlib
                    id_hash = int(hashlib.md5(nome.encode()).hexdigest()[:8], 16)
                    
                    resultados.append({
                        "id": id_hash,
                        "nome": nome,
                        "musculo": musculo_exibicao
                    })
        
        print(f"📊 Resultados encontrados: {len(resultados)}")
        return jsonify(resultados)
        
    except Exception as e:
        print(f"❌ Erro ao buscar catálogo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@api_bp.route("/api/verificar-treino")
def api_verificar_treino():
    treino_id = request.args.get("id", "").upper()
    treinos = load_json("treinos.json")
    
    existe = any(t["id"] == treino_id for t in treinos)
    
    return jsonify({"existe": existe})

@api_bp.route("/api/versao-exercicios/<int:versao_id>")
def api_versao_exercicios(versao_id):
    """API para retornar os exercícios de uma versão"""
    from utils import get_todos_exercicios_da_versao
    exercicios = get_todos_exercicios_da_versao(versao_id)
    
    resultado = []
    for ex in exercicios:
        resultado.append({
            "id": ex["id"],
            "nome": ex["nome"],
            "musculo": ex["musculo"],
            "treino": ex["treino"]
        })
    
    return jsonify(resultado)

@api_bp.route("/api/versao-detalhes/<int:versao_id>")
def api_versao_detalhes(versao_id):
    """API para retornar detalhes de uma versão específica"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v["id"] == versao_id), None)
    
    if not versao:
        return jsonify({"error": "Versão não encontrada"}), 404
    
    return jsonify({
        "id": versao["id"],
        "versao": versao.get("versao", 0),
        "descricao": versao.get("descricao", ""),
        "data_inicio": versao.get("data_inicio"),
        "data_fim": versao.get("data_fim"),
        "treinos": versao.get("treinos", {})
    })

@api_bp.route("/api/evolucao/<int:exercicio_id>")
def api_evolucao_exercicio(exercicio_id):
    registros = load_json("registros.json")
    exercicios = load_json("exercicios.json")
    
    exercicio = next((e for e in exercicios if e["id"] == exercicio_id), None)
    if not exercicio:
        return jsonify({"error": "Exercício não encontrado"}), 404
    
    registros_exercicio = [
        r for r in registros if r["exercicio_id"] == exercicio_id
    ]
    
    registros_exercicio.sort(key=lambda x: (x["periodo"], x["semana"]))
    
    dados = []
    for r in registros_exercicio:
        series = get_series_from_registro(r)
        media_carga, media_reps = calcular_media_series(series)
        volume_total = calcular_volume_total(series)
        
        dados.append({
            "sessao": f"{r['periodo']} - S{r['semana']}",
            "series": series,
            "media_carga": media_carga,
            "media_reps": media_reps,
            "volume_total": volume_total,
            "num_series": len(series)
        })
    
    return jsonify({
        "exercicio": exercicio["nome"],
        "dados": dados
    })
    
@api_bp.route("/api/criar-exercicio", methods=["POST"])
def api_criar_exercicio():
    """Cria um novo exercício e retorna o ID"""
    data = request.json
    
    if not data or not data.get("nome"):
        return jsonify({"success": False, "error": "Nome é obrigatório"}), 400
    
    exercicios = load_json("exercicios.json")
    
    novo_id = max([e["id"] for e in exercicios], default=0) + 1
    
    novo_exercicio = {
        "id": novo_id,
        "nome": data["nome"],
        "musculo": data.get("musculo", "Outros"),
        "treino": data.get("treino", "")
    }
    
    exercicios.append(novo_exercicio)
    exercicios.sort(key=lambda x: x["nome"])
    save_json("exercicios.json", exercicios)
    
    return jsonify({"success": True, "id": novo_id})