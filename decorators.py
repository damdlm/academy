from flask_login import login_required

@admin_bp.route("/gerenciar")
@login_required
def gerenciar():
    # ... código existente ...