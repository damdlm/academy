"""Registro de todos os blueprints da aplicação"""

import logging
from .main_routes import main_bp
from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .register_routes import register_bp
from .stats_routes import stats_bp
from .version_routes import version_bp
from .api_routes import api_bp

logger = logging.getLogger(__name__)

def register_all_routes(app):
    """Registra todos os blueprints no app Flask"""
    blueprints = [
        (main_bp, ''),
        (auth_bp, '/auth'),
        (admin_bp, '/admin'),
        (register_bp, '/registrar'),
        (stats_bp, '/estatisticas'),
        (version_bp, '/version'),
        (api_bp, '/api')
    ]
    
    for blueprint, url_prefix in blueprints:
        try:
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            app.logger.info(f"Blueprint {blueprint.name} registrado em {url_prefix or '/'}")
        except Exception as e:
            app.logger.error(f"Erro ao registrar {blueprint.name}: {e}")
    
    # Log de todas as rotas em modo debug
    if app.debug:
        app.logger.debug("\nRotas disponíveis:")
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
            if rule.endpoint != 'static':
                app.logger.debug(f"  {rule.endpoint}: {rule.rule}")