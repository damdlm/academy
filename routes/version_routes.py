from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime
from services.versao_service import VersaoService
from services.treino_service import TreinoService
from services.exercicio_service import ExercicioService
from services.musculo_service import MusculoService
from utils.format_utils import formatar_data, data_atual_iso
import logging

version_bp = Blueprint('version', __name__)
logger = logging.getLogger(__name__)

@version_bp.route("/gerenciar-versoes")
@login_required
def gerenciar_versoes_global():
    """Página principal de versões"""
    versoes = VersaoService.get_all()
    exercicios = ExercicioService.get_all()
    treinos = TreinoService.get_all()
    musculos = MusculoService.get_all_nomes()
    
    # Formatar versões
    versoes_formatadas = []
    for v in versoes:
        versoes_formatadas.append({
            "id": v.id,
            "versao": v.numero_versao,
            "descricao": v.descricao,
            "data_inicio": v.data_inicio.isoformat() if v.data_inicio else None,
            "data_fim": v.data_fim.isoformat() if v.data_fim else None,
            "data_inicio_formatada": formatar_data(v.data_inicio.isoformat() if v.data_inicio else None),
            "data_fim_formatada": formatar_data(v.data_fim.isoformat() if v.data_fim else None),
            "treinos": VersaoService.get_treinos(v.id)
        })
    
    return render_template("version/gerenciar_versoes_global.html",
                         versoes=versoes_formatadas,
                         exercicios=exercicios,
                         treinos=treinos,
                         musculos=musculos)

@version_bp.route("/salvar/versao", methods=["POST"])
@login_required
def salvar_versao_global():
    """Cria nova versão"""
    descricao = request.form["descricao"]
    data_inicio = datetime.strptime(request.form["data_inicio"], '%Y-%m-%d').date()
    data_fim_str = request.form.get("data_fim")
    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else None
    
    versao_ativa = VersaoService.get_ativa()
    if versao_ativa and not data_fim:
        flash(f"Já existe uma versão ativa. Finalize-a antes de criar outra.", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    nova_versao = VersaoService.create(descricao, data_inicio, data_fim)
    
    if nova_versao:
        logger.info(f"Nova versão criada: {nova_versao.numero_versao}")
        flash(f"Nova versão criada com sucesso!", "success")
    else:
        flash("Erro ao criar versão!", "danger")
    
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/ver/<int:versao_id>", methods=["GET", "POST"])
@login_required
def ver_versao(versao_id):
    """Visualiza e edita uma versão"""
    versao = VersaoService.get_by_id(versao_id)
    
    if not versao:
        flash("Versão não encontrada!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    # Processar POST do formulário
    if request.method == "POST":
        versao.descricao = request.form["descricao"]
        versao.data_inicio = datetime.strptime(request.form["data_inicio"], '%Y-%m-%d').date()
        data_fim_str = request.form.get("data_fim")
        versao.data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else None
        
        from models import db
        db.session.commit()
        logger.info(f"Versão {versao_id} atualizada")
        flash(f"Versão {versao.numero_versao} atualizada!", "success")
        return redirect(url_for("version.ver_versao", versao_id=versao_id))
    
    # Formatar para template
    versao_dict = {
        "id": versao.id,
        "versao": versao.numero_versao,
        "descricao": versao.descricao,
        "data_inicio": versao.data_inicio.isoformat() if versao.data_inicio else None,
        "data_fim": versao.data_fim.isoformat() if versao.data_fim else None,
        "data_inicio_formatada": formatar_data(versao.data_inicio.isoformat() if versao.data_inicio else None),
        "data_fim_formatada": formatar_data(versao.data_fim.isoformat() if versao.data_fim else None),
        "treinos": VersaoService.get_treinos(versao_id)
    }
    
    exercicios = ExercicioService.get_all()
    treinos = TreinoService.get_all()
    musculos = MusculoService.get_all_nomes()
    
    return render_template("version/ver_versao.html",
                         versao=versao_dict,
                         exercicios=exercicios,
                         treinos=treinos,
                         musculos=musculos)

@version_bp.route("/finalizar/<int:versao_id>")
@login_required
def finalizar_versao_global(versao_id):
    """Finaliza uma versão"""
    versao = VersaoService.get_by_id(versao_id)
    
    if not versao:
        flash("Versão não encontrada!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    if versao.data_fim:
        flash(f"Versão já finalizada em {formatar_data(versao.data_fim.isoformat())}.", "warning")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    data_atual = datetime.now().date()
    
    if VersaoService.finalizar(versao_id, data_atual):
        logger.info(f"Versão {versao_id} finalizada")
        flash(f"Versão {versao.numero_versao} finalizada!", "success")
    else:
        flash(f"Erro ao finalizar versão!", "danger")
    
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/clonar/<int:versao_id>")
@login_required
def clonar_versao_global(versao_id):
    """Clona uma versão"""
    from services.versao_service import VersaoService
    
    if VersaoService.clone(versao_id):
        logger.info(f"Versão {versao_id} clonada")
        flash(f"Versão clonada com sucesso!", "success")
    else:
        flash(f"Erro ao clonar versão!", "danger")
    
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/api/criar-treino", methods=["POST"])
@login_required
def api_criar_treino():
    """API para criar treino via AJAX"""
    data = request.get_json()
    
    treino_codigo = data.get('id', '').upper()
    nome = data.get('nome', '')
    descricao = data.get('descricao', '')
    
    if not treino_codigo or not nome:
        return jsonify({"success": False, "error": "ID e nome são obrigatórios"}), 400
    
    # Verificar se já existe
    existente = TreinoService.get_by_codigo(treino_codigo)
    if existente:
        return jsonify({"success": False, "error": f"Treino {treino_codigo} já existe!"}), 400
    
    novo_treino = TreinoService.create(treino_codigo, nome, descricao)
    
    if novo_treino:
        logger.info(f"Treino {treino_codigo} criado via API")
        return jsonify({
            "success": True, 
            "id": novo_treino.id,
            "codigo": novo_treino.codigo,
            "nome": novo_treino.nome
        })
    else:
        return jsonify({"success": False, "error": "Erro ao salvar no banco de dados"}), 500