import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/fitlog_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chave secreta
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-do-not-use-in-production')
    
    # Configurações de sessão
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de segurança
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'password-salt')
    
    # Configurações de debug
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    TESTING = False
    
    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')