import os
import sys
import io
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User

# Configurar encoding para toda a aplicação
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Inicializar extensões
login_manager = LoginManager()
csrf = CSRFProtect()

def setup_logging(app):
    """Configura logging da aplicação"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/fitlog.log', maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('FitLog iniciado')

def create_app(config_class=Config):
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configurar encoding
    app.config['JSON_AS_ASCII'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.json.ensure_ascii = False  # Garantir que JSON preserve acentos
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Erro ao carregar usuário {user_id}: {e}")
            db.session.rollback()
            return None
    
    # Configurar logging
    setup_logging(app)
    
    # Configurar middlewares
    from middleware.logging_middleware import setup_middleware
    setup_middleware(app)
    
    # Criar tabelas e usuário admin
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Tabelas verificadas/criadas")
        except Exception as e:
            app.logger.warning(f"Erro ao criar tabelas: {e}")
            db.session.rollback()
        
        # Criar admin se necessário
        if User.query.count() == 0:
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin = User(
                username='admin',
                email='admin@fitlog.com',
                is_admin=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Usuário admin criado")
    
    # Registrar blueprints
    from routes import register_all_routes
    register_all_routes(app)
    
    # Context processor para funções utilitárias
    from utils.format_utils import (
        data_atual_iso, 
        data_atual_formatada, 
        formatar_data, 
        formatar_data_para_input
    )
    
    @app.context_processor
    def utility_processor():
        """Disponibiliza funções utilitárias para todos os templates"""
        return dict(
            data_atual_iso=data_atual_iso,
            data_atual_formatada=data_atual_formatada,
            formatar_data=formatar_data,
            formatar_data_para_input=formatar_data_para_input
        )
    
    return app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FitLog - Sistema de Controle de Treinos".center(60))
    print("=" * 60)
    print(f"🔧 Modo: {'Debug' if app.debug else 'Produção'}")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado")
        sys.exit(0)