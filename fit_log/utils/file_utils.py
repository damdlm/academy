import json
from pathlib import Path

# Cache para melhor performance
_ultima_carga_cache = {}

def load_json(file):
    """Carrega um arquivo JSON da pasta storage"""
    from app import BASE
    path = BASE / file
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(file, data):
    """Salva dados em um arquivo JSON na pasta storage"""
    from app import BASE
    path = BASE / file
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def clear_cache():
    """Limpa o cache (útil após novos registros)"""
    global _ultima_carga_cache
    _ultima_carga_cache.clear()

def get_periodos_existentes():
    """Retorna lista de períodos com registros"""
    registros = load_json("registros.json")
    return sorted(set(r["periodo"] for r in registros), reverse=True)