from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from services.treino_service import TreinoService
from services.versao_service import VersaoService
from services.exercicio_service import ExercicioService
from services.registro_service import RegistroService
import logging

register_bp = Blueprint('register', __name__)
logger = logging.getLogger(__name__)

@register_bp.route("/registrar-treino", methods=["GET", "POST"])
@login_required
def registrar_treino():
    """Página de registro de treino"""
    treinos = TreinoService.get_all()
    versoes = VersaoService.get_all()

    treino = request.values.get("treino")
    periodo = request.values.get("periodo")
    semana = request.values.get("semana")

    # Validação de versão ativa
    versao_ativa = None
    erro_versao = None
    versao_global_id = None
    
    if periodo:
        versao_ativa = VersaoService.get_ativa(periodo)
        if not versao_ativa:
            erro_versao = f"Não há versão ativa para o período {periodo}."
        elif versao_ativa.data_fim:
            erro_versao = f"A versão {versao_ativa.numero_versao} foi finalizada em {versao_ativa.data_fim}."
        else:
            versao_global_id = versao_ativa.id
    
    if erro_versao:
        flash(erro_versao, "warning")
        versao_ativa = None
        exercicios_treino = []
    else:
        exercicios_treino = []
        if versao_global_id and treino:
            exercicios_treino = VersaoService.get_exercicios(versao_global_id, treino)

    registros_map = {}
    historico_series = {}
    
    if treino and periodo and semana and versao_global_id:
        registros = RegistroService.get_all({
            'treino_id': treino,
            'periodo': periodo,
            'semana': int(semana),
            'versao_id': versao_global_id
        })
        
        registros_map = {r.exercicio_id: r for r in registros}
        
        for ex in exercicios_treino:
            ultimas = ExercicioService.get_ultimas_series(ex.id, versao_id=versao_global_id, limite=1)
            if ultimas:
                historico_series[ex.id] = ultimas

    if request.method == "POST" and "salvar" in request.form:
        dados_exercicios = {}

        for ex in exercicios_treino:
            try:
                num_series = int(request.form.get(f"num_series_{ex.id}", 3))
                if num_series < 1 or num_series > 10:
                    num_series = 3
            except (ValueError, TypeError):
                num_series = 3
                
            carga = request.form.get(f"carga_{ex.id}")
            reps = request.form.get(f"reps_{ex.id}")
            
            if carga and reps and carga.strip() and reps.strip():
                try:
                    carga_float = float(carga)
                    reps_int = int(reps)
                    
                    if carga_float >= 0 and reps_int >= 0:
                        dados_exercicios[ex.id] = {
                            'carga': carga_float,
                            'repeticoes': reps_int,
                            'num_series': num_series,
                            'data_registro': datetime.now()
                        }
                except (ValueError, TypeError):
                    continue

        if dados_exercicios:
            if RegistroService.salvar_registros(treino, versao_global_id, periodo, int(semana), dados_exercicios):
                logger.info(f"Treino {treino} - Semana {semana} salvo")
                flash(f"Treino {treino} - Semana {semana} salvo com sucesso!", "success")
                return redirect(url_for("main.index"))
            else:
                flash("Erro ao salvar registros!", "danger")
        else:
            flash("Nenhum dado válido para salvar!", "warning")

    periodos_existentes = RegistroService.get_periodos_existentes()

    return render_template(
        "register/registrar_treino.html",
        treinos=treinos,
        exercicios=exercicios_treino,
        registros=registros_map,
        historico_series=historico_series,
        periodos_existentes=periodos_existentes,
        treino=treino,
        periodo=periodo,
        semana=semana,
        versao_ativa=versao_ativa,
        versoes=versoes
    )