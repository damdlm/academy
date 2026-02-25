"""Middleware para verificação de autenticação"""

from flask import request, redirect, url_for, flash
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """Middleware que verifica autenticação para rotas protegidas"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Verificar se a rota requer autenticação
        path = environ.get('PATH_INFO', '')
        
        # Rotas públicas
        public_paths = ['/auth/login', '/auth/register', '/static']
        
        is_public = any(path.startswith(p) for p in public_paths)
        
        if not is_public and not self._is_authenticated(environ):
            # Redirecionar para login
            environ['PATH_INFO'] = '/auth/login'
            environ['QUERY_STRING'] = f'next={path}'
        
        return self.app(environ, start_response)
    
    def _is_authenticated(self, environ):
        """Verifica se o usuário está autenticado"""
        # Esta é uma simplificação - em produção, use flask_login
        from flask import session
        return session.get('user_id') is not None