import json
from pathlib import Path

BASE = Path("storage")
catalogo_path = BASE / "exercises-ptbr-full-translation.json"

print(f"Verificando arquivo: {catalogo_path}")
print(f"Arquivo existe: {catalogo_path.exists()}")

if not catalogo_path.exists():
    print("Arquivo não encontrado!")
    exit()

with open(catalogo_path, 'r', encoding='utf-8') as f:
    catalogo = json.load(f)

print(f"Total de exercícios: {len(catalogo)}")

# Coletar todos os músculos primários
musculos = set()
musculos_por_exercicio = {}

for ex in catalogo:
    nome = ex.get('name', 'Sem nome')
    primary = ex.get('primaryMuscles', [])
    
    for m in primary:
        musculos.add(m.lower())
        
        # Guardar exemplo de exercício para cada músculo
        if m.lower() not in musculos_por_exercicio:
            musculos_por_exercicio[m.lower()] = nome

print("\n" + "="*50)
print("MÚSCULOS ENCONTRADOS NO CATÁLOGO:")
print("="*50)

# Mapeamento sugerido para português
sugestoes = {
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

for musculo in sorted(musculos):
    exemplo = musculos_por_exercicio.get(musculo, "N/A")
    sugestao = sugestoes.get(musculo, "⚠️ Não mapeado")
    print(f"  • {musculo:20} → {sugestao:20} (ex: {exemplo})")

print("="*50)
print(f"Total de músculos únicos: {len(musculos)}")