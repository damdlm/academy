"""
Pacote de rotas da aplicação FitLog
"""

from .main_routes import main_bp
from .register_routes import register_bp
from .stats_routes import stats_bp
from .admin_routes import admin_bp
from .version_routes import version_bp
from .api_routes import api_bp

__all__ = ['main_bp', 'register_bp', 'stats_bp', 'admin_bp', 'version_bp', 'api_bp']

def register_all_routes(app):
    """Registra todos os blueprints no app Flask"""
    print("📦 Registrando blueprints...")
    
    try:
        app.register_blueprint(main_bp)
        print("  ✅ main_bp registrado em /")
        
        app.register_blueprint(register_bp)
        print("  ✅ register_bp registrado em /registrar")
        
        app.register_blueprint(stats_bp)
        print("  ✅ stats_bp registrado em /estatisticas")
        
        app.register_blueprint(admin_bp)
        print("  ✅ admin_bp registrado em /gerenciar")
        
        app.register_blueprint(version_bp)
        print("  ✅ version_bp registrado em /gerenciar/versoes-global")
        
        app.register_blueprint(api_bp)
        print("  ✅ api_bp registrado em /api")
        
        print("\n📋 Rotas disponíveis:")
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
            if rule.endpoint != 'static':
                print(f"  {rule.endpoint}: {rule.rule}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao registrar blueprints: {e}")
        import traceback
        traceback.print_exc()
        return False