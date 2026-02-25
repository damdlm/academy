from app import create_app
from models import db
from utils.db_utils import get_treinos, get_exercicios, get_versoes

app = create_app()
with app.app_context():
    print("=" * 50)
    print("TESTANDO FUNÇÕES DO BANCO")
    print("=" * 50)
    
    # Testar treinos
    try:
        treinos = get_treinos()
        print(f"✅ get_treinos: {len(treinos)} treinos encontrados")
        for t in treinos:
            print(f"   - {t.id}: {t.descricao}")
    except Exception as e:
        print(f"❌ get_treinos erro: {e}")
    
    # Testar exercícios
    try:
        exercicios = get_exercicios()
        print(f"\n✅ get_exercicios: {len(exercicios)} exercícios encontrados")
        for e in exercicios[:5]:  # Mostrar só 5
            print(f"   - {e.id}: {e.nome}")
    except Exception as e:
        print(f"❌ get_exercicios erro: {e}")
    
    # Testar versões
    try:
        versoes = get_versoes()
        print(f"\n✅ get_versoes: {len(versoes)} versões encontradas")
        for v in versoes:
            print(f"   - Versão {v.numero_versao}: {v.descricao}")
    except Exception as e:
        print(f"❌ get_versoes erro: {e}")