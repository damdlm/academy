import json
from pathlib import Path

BASE = Path("storage")

def migrar_versoes_para_global():
    """Função utilitária para migrar versões antigas para o formato global"""
    arquivo_versoes = BASE / "versoes_treino.json"
    
    if not arquivo_versoes.exists():
        print("Arquivo de versões não encontrado!")
        return
    
    with open(arquivo_versoes, 'r', encoding='utf-8') as f:
        versoes = json.load(f)
    
    # Verifica se já está no formato novo
    if any('treinos' in v for v in versoes):
        print("Arquivo já está no formato global")
        return versoes
    
    # Agrupa versões por número/versão
    versoes_por_numero = {}
    for v in versoes:
        if 'treino_id' in v and 'versao' in v:
            key = v['versao']
            if key not in versoes_por_numero:
                versoes_por_numero[key] = {
                    "versao": key,
                    "descricao": f"Versão {key} (migrada)",
                    "data_inicio": v.get("data_inicio", "2024-01-01"),
                    "data_fim": v.get("data_fim"),
                    "treinos": {}
                }
            versoes_por_numero[key]["treinos"][v["treino_id"]] = v.get("exercicios", [])
    
    # Converte para lista
    versoes_globais = []
    for i, (num, v) in enumerate(versoes_por_numero.items()):
        v["id"] = i + 1
        versoes_globais.append(v)
    
    # Salva o arquivo
    with open(arquivo_versoes, 'w', encoding='utf-8') as f:
        json.dump(versoes_globais, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(versoes_globais)} versões migradas com sucesso!")
    return versoes_globais

if __name__ == "__main__":
    migrar_versoes_para_global()