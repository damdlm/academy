from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services.treino_service import TreinoService
from services.exercicio_service import ExercicioService
from services.musculo_service import MusculoService
from services.versao_service import VersaoService
from utils.exercise_utils import buscar_musculo_no_catalogo
from models import db, Exercicio, RegistroTreino, HistoricoTreino
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route("/gerenciar")
@login_required
def gerenciar():
    """Página de gerenciamento de treinos e exercícios"""
    treinos = TreinoService.get_all()
    
    # Carregar exercícios com relações em uma única consulta
    exercicios = Exercicio.query.options(
        joinedload(Exercicio.musculo_ref),
        joinedload(Exercicio.treino_ref)
    ).filter_by(user_id=current_user.id).order_by(Exercicio.nome).all()
    
    musculos = MusculoService.get_all_nomes()
    
    exercicios_por_treino = {}
    for ex in exercicios:
        treino_id = ex.treino_id
        exercicios_por_treino[treino_id] = exercicios_por_treino.get(treino_id, 0) + 1
    
    # Buscar todas as últimas cargas em uma única consulta otimizada
    # Subquery para encontrar o registro mais recente por exercício
    subq = db.session.query(
        RegistroTreino.exercicio_id,
        func.max(RegistroTreino.data_registro).label('max_data')
    ).filter_by(user_id=current_user.id).group_by(RegistroTreino.exercicio_id).subquery()
    
    # Buscar a primeira série do registro mais recente
    ultimas_cargas_query = db.session.query(
        RegistroTreino.exercicio_id,
        HistoricoTreino.carga
    ).join(
        subq, 
        (RegistroTreino.exercicio_id == subq.c.exercicio_id) & 
        (RegistroTreino.data_registro == subq.c.max_data)
    ).join(
        HistoricoTreino, 
        HistoricoTreino.registro_id == RegistroTreino.id
    ).filter(
        HistoricoTreino.ordem == 1  # Primeira série
    ).all()
    
    ultimas_cargas = {ex_id: float(carga) for ex_id, carga in ultimas_cargas_query}
    
    return render_template("admin/gerenciar_treinos.html",
                         treinos=treinos,
                         exercicios=exercicios,
                         musculos=musculos,
                         exercicios_por_treino=exercicios_por_treino,
                         ultimas_cargas=ultimas_cargas)

@admin_bp.route("/salvar/treino", methods=["POST"])
@login_required
def salvar_treino():
    """Salva um novo treino"""
    codigo = request.form["id"].upper()
    nome = request.form.get("nome", codigo)
    descricao = request.form["descricao"]
    
    # Verificar se já existe
    existente = TreinoService.get_by_codigo(codigo)
    if existente:
        flash(f"Treino {codigo} já existe!", "danger")
        return redirect(url_for("admin.gerenciar"))
    
    treino = TreinoService.create(codigo, nome, descricao)
    
    if treino:
        logger.info(f"Treino {codigo} criado")
        flash(f"Treino {codigo} criado com sucesso!", "success")
    else:
        flash("Erro ao criar treino!", "danger")
    
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/editar/treino", methods=["POST"])
@login_required
def editar_treino():
    """Edita um treino existente"""
    treino_id = request.form["id_original"]
    novo_codigo = request.form["id"].upper()
    novo_nome = request.form.get("nome", novo_codigo)
    nova_descricao = request.form["descricao"]
    
    treino = TreinoService.update(treino_id, novo_codigo, novo_nome, nova_descricao)
    
    if treino:
        logger.info(f"Treino {treino_id} atualizado")
        flash(f"Treino atualizado com sucesso!", "success")
    else:
        flash(f"Erro ao atualizar treino!", "danger")
    
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/salvar/exercicio", methods=["POST"])
@login_required
def salvar_exercicio():
    """Salva um novo exercício"""
    nome_exercicio = request.form["nome"]
    musculo = request.form["musculo"]
    treino = request.form["treino"]
    descricao = request.form.get("descricao", "")
    
    musculo_final = musculo if musculo and musculo.strip() else None
    
    if not musculo_final:
        musculo_encontrado = buscar_musculo_no_catalogo(nome_exercicio)
        if musculo_encontrado:
            musculo_final = musculo_encontrado
            flash(f"Músculo '{musculo_final}' encontrado no catálogo!", "info")
        else:
            musculo_final = "Outros"
            flash("Usando músculo 'Outros'.", "warning")
    
    treino_id = treino if treino else None
    
    exercicio = ExercicioService.create(
        nome=nome_exercicio,
        musculo_nome=musculo_final,
        treino_id=treino_id,
        descricao=descricao
    )
    
    if exercicio:
        logger.info(f"Exercício '{nome_exercicio}' criado")
        flash(f"Exercício '{nome_exercicio}' criado!", "success")
    else:
        flash("Erro ao criar exercício!", "danger")
    
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/editar/exercicio", methods=["POST"])
@login_required
def editar_exercicio():
    """Edita um exercício existente"""
    exercicio_id = int(request.form["id"])
    nome_exercicio = request.form["nome"]
    musculo = request.form["musculo"]
    treino = request.form["treino"]
    descricao = request.form.get("descricao", "")
    
    if not musculo or musculo == "":
        musculo_encontrado = buscar_musculo_no_catalogo(nome_exercicio)
        if musculo_encontrado:
            musculo = musculo_encontrado
            flash(f"Músculo atualizado para '{musculo}'", "info")
        else:
            exercicio_original = ExercicioService.get_by_id(exercicio_id)
            if exercicio_original and exercicio_original.musculo_ref:
                musculo = exercicio_original.musculo_ref.nome_exibicao
            else:
                musculo = "Outros"
    
    treino_id = treino if treino else None
    
    exercicio = ExercicioService.update(
        exercicio_id=exercicio_id,
        nome=nome_exercicio,
        musculo_nome=musculo,
        treino_id=treino_id,
        descricao=descricao
    )
    
    if exercicio:
        logger.info(f"Exercício {exercicio_id} atualizado")
        flash("Exercício atualizado com sucesso!", "success")
    else:
        flash("Erro ao atualizar exercício!", "danger")
    
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/excluir/treino/<int:treino_id>")
@login_required
def excluir_treino(treino_id):
    """Exclui um treino"""
    if TreinoService.delete(treino_id):
        logger.info(f"Treino {treino_id} excluído")
        flash(f"Treino excluído com sucesso!", "success")
    else:
        flash(f"Erro ao excluir treino!", "danger")
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/excluir/exercicio/<int:exercicio_id>")
@login_required
def excluir_exercicio(exercicio_id):
    """Exclui um exercício"""
    exercicio = ExercicioService.get_by_id(exercicio_id)
    nome = exercicio.nome if exercicio else "Exercício"
    
    if ExercicioService.delete(exercicio_id):
        logger.info(f"Exercício '{nome}' excluído")
        flash(f"'{nome}' excluído com sucesso!", "success")
    else:
        flash(f"Erro ao excluir '{nome}'!", "danger")
    
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/exercicio/detalhes/<int:exercicio_id>")
@login_required
def exercicio_detalhes(exercicio_id):
    """Detalhes de um exercício"""
    exercicio = ExercicioService.get_by_id(exercicio_id, load_relations=True)
    
    if not exercicio:
        flash("Exercício não encontrado!", "danger")
        return redirect(url_for("admin.gerenciar"))
    
    from utils.version_utils import verificar_exercicio_em_versoes
    versoes = verificar_exercicio_em_versoes(exercicio_id)
    
    return render_template("admin/exercicio_detalhes.html",
                         exercicio=exercicio,
                         versoes=versoes)

@admin_bp.route("/api/verificar-treino")
@login_required
def api_verificar_treino():
    """API para verificar se código de treino existe"""
    codigo = request.args.get("id", "").upper()
    treino = TreinoService.get_by_codigo(codigo)
    return jsonify({"existe": treino is not None})