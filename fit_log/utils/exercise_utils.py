import json
from pathlib import Path
from .file_utils import load_json

def buscar_musculo_no_catalogo(nome_exercicio):
    """
    Busca o músculo primário de um exercício no catálogo completo.
    Retorna o nome do músculo em português ou None se não encontrar.
    """
    from app import BASE
    catalogo_path = BASE / "exercises-ptbr-full-translation.json"
    
    if not catalogo_path.exists():
        print("Arquivo de catálogo não encontrado!")
        return None
    
    try:
        with open(catalogo_path, 'r', encoding='utf-8') as f:
            catalogo = json.load(f)
        
        nome_busca = nome_exercicio.lower().strip()
        
        # 1. Correspondência exata
        for ex in catalogo:
            nome_catalogo = ex.get('name', '').lower().strip()
            if nome_catalogo == nome_busca:
                primary_muscles = ex.get('primaryMuscles', [])
                if primary_muscles and len(primary_muscles) > 0:
                    return primary_muscles[0]
        
        # 2. Nome do catálogo CONTÉM o nome buscado
        for ex in catalogo:
            nome_catalogo = ex.get('name', '').lower()
            if nome_busca in nome_catalogo:
                primary_muscles = ex.get('primaryMuscles', [])
                if primary_muscles and len(primary_muscles) > 0:
                    return primary_muscles[0]
        
        # 3. Nome buscado CONTÉM o nome do catálogo
        for ex in catalogo:
            nome_catalogo = ex.get('name', '').lower()
            if nome_catalogo in nome_busca:
                primary_muscles = ex.get('primaryMuscles', [])
                if primary_muscles and len(primary_muscles) > 0:
                    return primary_muscles[0]
        
    except Exception as e:
        print(f"Erro ao buscar no catálogo: {e}")
    
    return None

def get_series_from_registro(registro):
    """Retorna as séries de um registro, convertendo formato antigo se necessário"""
    if "series" in registro:
        return registro["series"]
    elif "carga" in registro and "repeticoes" in registro:
        return [{"carga": registro["carga"], "repeticoes": registro["repeticoes"]}]
    return []

def calcular_media_series(series):
    """Calcula média de carga e repetições das séries"""
    if not series:
        return 0, 0
    media_carga = sum(s["carga"] for s in series) / len(series)
    media_reps = sum(s["repeticoes"] for s in series) / len(series)
    return round(media_carga, 1), round(media_reps, 1)

def calcular_volume_total(series):
    """Calcula volume total somando todas as séries"""
    return sum(s["carga"] * s["repeticoes"] for s in series)