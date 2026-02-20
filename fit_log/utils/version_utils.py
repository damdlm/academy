from .file_utils import load_json, save_json
from .date_utils import converter_periodo_para_data
from .exercise_utils import get_series_from_registro

# ===== VERSÕES GLOBAIS (NOVO FORMATO COM TREINOS DENTRO) =====

def get_versoes_globais():
    """Retorna todas as versões globais"""
    return load_json("versoes_treino.json")

def get_versao_ativa(periodo):
    """
    Retorna a versão global que estava ativa em um determinado período
    """
    versoes = get_versoes_globais()
    
    if not versoes:
        return None
    
    try:
        data_periodo = converter_periodo_para_data(periodo)
    except Exception as e:
        print(f"Erro ao converter período '{periodo}': {e}")
        return versoes[-1] if versoes else None
    
    versoes_ordenadas = sorted(versoes, key=lambda x: x.get("data_inicio", "1900-01-01"))
    
    for v in versoes_ordenadas:
        data_inicio = v.get("data_inicio", "1900-01-01")
        data_fim = v.get("data_fim")
        
        if data_inicio <= data_periodo:
            if data_fim is None or data_fim >= data_periodo:
                return v
    
    return versoes_ordenadas[-1] if versoes_ordenadas else None

def get_treinos_da_versao(versao_id):
    """Retorna todos os treinos de uma versão específica"""
    versoes = get_versoes_globais()
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao:
        return {}
    
    return versao.get("treinos", {})

def get_exercicios_do_treino(versao_id, treino_id):
    """Retorna os exercícios de um treino específico em uma versão"""
    versoes = get_versoes_globais()
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return []
    
    treino = versao["treinos"].get(treino_id)
    if not treino:
        return []
    
    exercicios_ids = treino.get("exercicios", [])
    exercicios = load_json("exercicios.json")
    
    return [ex for ex in exercicios if ex["id"] in exercicios_ids]

def get_todos_exercicios_da_versao(versao_id):
    """Retorna todos os exercícios de todos os treinos em uma versão"""
    versoes = get_versoes_globais()
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return []
    
    todos_ids = []
    for treino_id, treino_data in versao["treinos"].items():
        todos_ids.extend(treino_data.get("exercicios", []))
    
    exercicios = load_json("exercicios.json")
    return [ex for ex in exercicios if ex["id"] in todos_ids]

# ===== FUNÇÕES PARA GERENCIAR TREINOS DENTRO DAS VERSÕES =====

def adicionar_treino_na_versao(versao_id, treino_id, nome_treino, descricao_treino, exercicios_ids):
    """Adiciona um novo treino em uma versão existente"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao:
        return False
    
    if 'treinos' not in versao:
        versao['treinos'] = {}
    
    versao['treinos'][treino_id] = {
        "nome": nome_treino,
        "descricao": descricao_treino,
        "exercicios": exercicios_ids or []
    }
    
    save_json("versoes_treino.json", versoes)
    return True

def verificar_versao_ativa(periodo=None):
    """
    Verifica se há uma versão ativa no período.
    Retorna (tem_ativa, versao, mensagem_erro)
    """
    versoes = get_versoes_globais()
    
    if not versoes:
        return False, None, "Nenhuma versão cadastrada. Crie uma versão primeiro."
    
    if not periodo:
        # Se não tem período, pega a versão atual (sem data_fim)
        versao_atual = next((v for v in versoes if v.get("data_fim") is None), None)
        if versao_atual:
            return True, versao_atual, None
        else:
            return False, None, "Não há versão ativa no momento. Crie uma nova versão ou finalize a anterior."
    
    # Se tem período, verifica versão ativa naquele período
    try:
        data_periodo = converter_periodo_para_data(periodo)
    except:
        return False, None, f"Período '{periodo}' inválido."
    
    for v in versoes:
        data_inicio = v.get("data_inicio", "1900-01-01")
        data_fim = v.get("data_fim")
        
        if data_inicio <= data_periodo:
            if data_fim is None or data_fim >= data_periodo:
                return True, v, None
    
    return False, None, f"Não há versão ativa para o período {periodo}."

def editar_treino_na_versao(versao_id, treino_id, nome_treino=None, descricao_treino=None, exercicios_ids=None):
    """Edita um treino existente em uma versão"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return False
    
    treino = versao['treinos'].get(treino_id)
    if not treino:
        return False
    
    if nome_treino is not None:
        treino['nome'] = nome_treino
    if descricao_treino is not None:
        treino['descricao'] = descricao_treino
    if exercicios_ids is not None:  # Agora atualiza quando recebe a lista
        treino['exercicios'] = exercicios_ids
    
    save_json("versoes_treino.json", versoes)
    return True

def remover_treino_da_versao(versao_id, treino_id):
    """Remove um treino de uma versão"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return False
    
    if treino_id in versao['treinos']:
        del versao['treinos'][treino_id]
        save_json("versoes_treino.json", versoes)
        return True
    
    return False

# ===== NOVAS FUNÇÕES PARA GERENCIAR EXERCÍCIOS DENTRO DOS TREINOS =====

def adicionar_exercicio_ao_treino(versao_id, treino_id, exercicio_id):
    """Adiciona um exercício existente a um treino específico dentro de uma versão"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return False
    
    treino = versao['treinos'].get(treino_id)
    if not treino:
        return False
    
    if 'exercicios' not in treino:
        treino['exercicios'] = []
    
    if exercicio_id not in treino['exercicios']:
        treino['exercicios'].append(exercicio_id)
        save_json("versoes_treino.json", versoes)
    
    return True

def remover_exercicio_do_treino(versao_id, treino_id, exercicio_id):
    """Remove um exercício de um treino específico dentro de uma versão"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return False
    
    treino = versao['treinos'].get(treino_id)
    if not treino or 'exercicios' not in treino:
        return False
    
    if exercicio_id in treino['exercicios']:
        treino['exercicios'].remove(exercicio_id)
        save_json("versoes_treino.json", versoes)
        return True
    
    return False

def reordenar_exercicios_do_treino(versao_id, treino_id, nova_ordem):
    """Reordena os exercícios de um treino (lista de IDs na nova ordem)"""
    versoes = load_json("versoes_treino.json")
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        return False
    
    treino = versao['treinos'].get(treino_id)
    if not treino:
        return False
    
    treino['exercicios'] = nova_ordem
    save_json("versoes_treino.json", versoes)
    return True

# ===== FUNÇÕES PARA VERIFICAR ONDE UM EXERCÍCIO É USADO =====

def verificar_exercicio_em_versoes(exercicio_id):
    """
    Verifica em quais versões e treinos um exercício está presente
    """
    versoes = get_versoes_globais()
    resultado = []
    
    for v in versoes:
        for treino_id, treino_data in v.get("treinos", {}).items():
            if exercicio_id in treino_data.get("exercicios", []):
                resultado.append({
                    "versao_id": v["id"],
                    "versao": v["versao"],
                    "versao_descricao": v["descricao"],
                    "treino_id": treino_id,
                    "treino_nome": treino_data.get("nome", treino_id),
                    "treino_descricao": treino_data.get("descricao", ""),
                    "data_inicio": v["data_inicio"],
                    "data_fim": v["data_fim"]
                })
    
    return resultado

# ===== FUNÇÕES DE MIGRAÇÃO =====

def migrar_versoes_para_novo_formato():
    """
    Função para migrar versões antigas para o novo formato com treinos detalhados
    """
    versoes = load_json("versoes_treino.json")
    
    # Se não houver versões, retorna lista vazia
    if not versoes:
        return []
    
    # Verifica se já está no novo formato
    for v in versoes:
        if 'treinos' in v and v['treinos']:
            primeiro_treino = next(iter(v['treinos'].values())) if v['treinos'] else None
            if primeiro_treino and isinstance(primeiro_treino, dict) and 'exercicios' in primeiro_treino:
                print("Arquivo já está no novo formato")
                return versoes
    
    # Converte para o novo formato
    novas_versoes = []
    for v in versoes:
        if 'treinos' in v and isinstance(v['treinos'], dict):
            novos_treinos = {}
            for treino_id, exercicios_ids in v['treinos'].items():
                # Se for lista, converte para dicionário
                if isinstance(exercicios_ids, list):
                    novos_treinos[treino_id] = {
                        "nome": f"Treino {treino_id}",
                        "descricao": f"Treino {treino_id}",
                        "exercicios": exercicios_ids
                    }
                # Se já for dicionário, mantém
                elif isinstance(exercicios_ids, dict):
                    novos_treinos[treino_id] = exercicios_ids
            v['treinos'] = novos_treinos
        novas_versoes.append(v)
    
    return novas_versoes

# ===== FUNÇÕES DE COMPATIBILIDADE (MANTIDAS PARA NÃO QUEBRAR O CÓDIGO) =====

def get_versoes_treino_antigo(treino_id=None):
    """Compatibilidade: retorna lista vazia"""
    return []

def get_versao_ativa_antiga(treino_id, periodo):
    """Compatibilidade: retorna None"""
    return None

def get_exercicios_por_versao_antiga(versao_id):
    """Compatibilidade: retorna lista vazia"""
    return []

def get_versoes_treino(treino_id=None):
    """Compatibilidade: redireciona para get_versoes_globais"""
    return get_versoes_globais()

def get_exercicios_por_versao(versao_id):
    """Compatibilidade: redireciona para get_todos_exercicios_da_versao"""
    return get_todos_exercicios_da_versao(versao_id)

def get_ultimas_series(exercicio_id, versao_global_id=None, versao_id=None, limite=1):
    """
    Obtém as últimas séries de um exercício
    """
    registros = load_json("registros.json")
    series_exercicio = []
    
    for r in reversed(registros):
        if r["exercicio_id"] == exercicio_id:
            # Filtra por versão global
            if versao_global_id is not None and r.get("versao_global_id") != versao_global_id:
                continue
                
            series = get_series_from_registro(r)
            if not series:
                continue
                
            series_exercicio.append({
                "periodo": r["periodo"],
                "semana": r["semana"],
                "series": series
            })
            if len(series_exercicio) >= limite:
                break
    
    return series_exercicio