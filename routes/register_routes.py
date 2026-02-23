from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from utils import (
    load_json, save_json, clear_cache, get_periodos_existentes,
    get_versao_ativa, get_exercicios_do_treino,
    get_ultimas_series, get_series_from_registro, verificar_versao_ativa
)

register_bp = Blueprint('register', __name__)

@register_bp.route("/registrar-treino", methods=["GET", "POST"])
def registrar_treino():
    """Registra um treino usando a versão ativa do período"""
    treinos = load_json("treinos.json")
    exercicios = load_json("exercicios.json")
    registros = load_json("registros.json")
    versoes = load_json("versoes_treino.json")

    treino = request.values.get("treino")
    periodo = request.values.get("periodo")
    semana = request.values.get("semana")

    # Validação de versão ativa
    versao_ativa = None
    erro_versao = None
    versao_global_id = None  # <--- INICIALIZA A VARIÁVEL AQUI
    
    if periodo:
        versao_ativa = get_versao_ativa(periodo)
        if not versao_ativa:
            erro_versao = f"Não há versão ativa para o período {periodo}. Crie uma versão primeiro."
        elif versao_ativa.get("data_fim"):
            erro_versao = f"A versão {versao_ativa['versao']} foi finalizada em {versao_ativa['data_fim']}. Não é possível registrar treinos neste período."
        else:
            versao_global_id = versao_ativa["id"]  # <--- SÓ ATRIBUI SE TIVER VERSÃO ATIVA
    
    # Se tem erro de versão, mostra mensagem e não carrega exercícios
    if erro_versao:
        flash(erro_versao, "warning")
        versao_ativa = None
        exercicios_treino = []
    else:
        # Carrega exercícios da versão ativa
        exercicios_treino = get_exercicios_do_treino(versao_global_id, treino) if versao_global_id and treino else []

    registros_map = {}
    historico_series = {}
    
    if treino and periodo and semana and versao_global_id:
        registros_map = {
            r["exercicio_id"]: r
            for r in registros
            if r["treino"] == treino
            and r["periodo"] == periodo
            and str(r["semana"]) == str(semana)
            and r.get("versao_global_id") == versao_global_id
        }
        
        for ex in exercicios_treino:
            ultimas = get_ultimas_series(ex["id"], versao_global_id=versao_global_id, limite=1)
            if ultimas:
                historico_series[ex["id"]] = ultimas[0]["series"]

    if request.method == "POST" and "salvar" in request.form:
        novos = []
        clear_cache()

        for ex in exercicios_treino:
            try:
                num_series = int(request.form.get(f"num_series_{ex['id']}", 3))
                if num_series < 1 or num_series > 10:
                    num_series = 3
            except (ValueError, TypeError):
                num_series = 3
                
            carga = request.form.get(f"carga_{ex['id']}")
            reps = request.form.get(f"reps_{ex['id']}")
            
            if carga is not None and reps is not None and carga != '' and reps != '':
                try:
                    carga_float = float(carga)
                    reps_int = int(reps)
                    
                    if carga_float >= 0 and reps_int >= 0:
                        series = []
                        for i in range(num_series):
                            series.append({
                                "carga": carga_float,
                                "repeticoes": reps_int
                            })
                        
                        novos.append({
                            "treino": treino,
                            "versao_global_id": versao_global_id,
                            "periodo": periodo,
                            "semana": int(semana),
                            "exercicio_id": ex["id"],
                            "series": series,
                            "num_series": num_series,
                            "data_registro": datetime.now().isoformat()
                        })
                except (ValueError, TypeError):
                    continue

        # Remove registros antigos do mesmo treino/semana/versão
        registros = [
            r for r in registros
            if not (
                r["treino"] == treino and
                r["periodo"] == periodo and
                r["semana"] == int(semana) and
                r.get("versao_global_id") == versao_global_id
            )
        ]

        registros.extend(novos)
        save_json("registros.json", registros)

        flash(f"Treino {treino} - Semana {semana} salvo com sucesso!", "success")
        return redirect(url_for("main.index"))

    return render_template(
        "registrar_treino.html",
        treinos=treinos,
        exercicios=exercicios_treino,
        registros=registros_map,
        historico_series=historico_series,
        periodos_existentes=get_periodos_existentes(),
        treino=treino,
        periodo=periodo,
        semana=semana,
        versao_ativa=versao_ativa,
        versoes=versoes
    )