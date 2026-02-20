from flask import Flask
from pathlib import Path
import sys
import os

# Adiciona o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Inicializa o app
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para flash messages

# Configuração do caminho base
BASE = Path("storage")

# Torna BASE acessível em outros módulos
app.config['BASE'] = BASE

# Importa e registra as rotas
try:
    print("📦 Importando rotas...")
    from routes import register_all_routes
    print("✅ Módulo routes importado com sucesso")
    
    register_all_routes(app)
    print("✅ Rotas registradas com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar módulo routes: {e}")
    print("📁 Verifique se o diretório 'routes' existe e contém __init__.py")
    
except Exception as e:
    print(f"❌ Erro ao registrar rotas: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask...")
    app.run(debug=True)