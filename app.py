from flask import Flask
from pathlib import Path
import sys
import os
from flask_login import LoginManager
from models import db, User

# Adiciona o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Inicializa o app
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Mude para uma chave segura

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitlog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db.init_app(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configuração do caminho base
BASE = Path("storage")
app.config['BASE'] = BASE

# Criar tabelas no banco de dados
with app.app_context():
    db.create_all()
    print("✅ Banco de dados inicializado")

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