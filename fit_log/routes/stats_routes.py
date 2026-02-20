from flask import Blueprint, render_template, jsonify, request
from utils import (
    load_json, get_series_from_registro, calcular_volume_total,
    calcular_estatisticas_musculo, calcular_estatisticas_treino
)

stats_bp = Blueprint('stats', __name__)

@stats_bp.route("/estatisticas")
def estatisticas():
    registros = load_json("registros.json")
    exercicios = load_json("exercicios.json")
    treinos = load_json("treinos.json")
    
    musculos = sorted(set(e["musculo"] for e in exercicios))
    musculo_stats = calcular_estatisticas_musculo(registros, exercicios)
    treino_stats = calcular_estatisticas_treino(treinos, exercicios, registros)
    
    return render_template("estatisticas.html",
                         musculo_stats=musculo_stats,
                         treino_stats=treino_stats,
                         treinos=treinos,
                         musculos=musculos)

@stats_bp.route("/visualizar/tabela")
def visualizar_tabela():
    treino_selecionado = request.args.get("treino", "")
    musculo_selecionado = request.args.get("musculo", "")
    ordenar = request.args.get("ordenar", "exercicio")
    semanas_filtro = request.args.get("semanas", "todas")
    
    registros = load_json("registros.json")
    exercicios = load_json("exercicios.json")
    treinos = load_json("treinos.json")
    
    musculos = sorted(set(e["musculo"] for e in exercicios))
    
    exercicios_filtrados = exercicios.copy()
    if treino_selecionado:
        exercicios_filtrados = [e for e in exercicios_filtrados if e["treino"] == treino_selecionado]
    if musculo_selecionado:
        exercicios_filtrados = [e for e in exercicios_filtrados if e["musculo"] == musculo_selecionado]
    
    if ordenar == "musculo":
        exercicios_filtrados.sort(key=lambda x: (x["musculo"], x["nome"]))
    else:
        exercicios_filtrados.sort(key=lambda x: (x["treino"], x["nome"]))
    
    registros_por_exercicio = {}
    for ex in exercicios_filtrados:
        registros_por_exercicio[ex["id"]] = {}
    
    for r in registros:
        if r["exercicio_id"] in registros_por_exercicio:
            key = f"{r['periodo']}_{r['semana']}"
            registros_por_exercicio[r["exercicio_id"]][key] = r
    
    semanas_set = set()
    for r in registros:
        semanas_set.add((r["periodo"], r["semana"], f"{r['periodo']}_{r['semana']}"))
    
    semanas = []
    for periodo, semana, key in semanas_set:
        semanas.append({
            "periodo": periodo,
            "semana": semana,
            "key": key
        })
    
    ordem_periodos = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    semanas.sort(key=lambda x: (ordem_periodos.index(x["periodo"]) if x["periodo"] in ordem_periodos else 999, x["semana"]))
    
    semanas_filtradas = []
    semanas_selecionadas_lista = []
    
    if semanas_filtro == "ultimas3":
        semanas_filtradas = semanas[-3:]
    elif semanas_filtro == "ultimas5":
        semanas_filtradas = semanas[-5:]
    elif semanas_filtro == "personalizado":
        for periodo, semana, key in semanas_set:
            if request.args.get(f"semana_{periodo}_{semana}"):
                semanas_filtradas.append({
                    "periodo": periodo,
                    "semana": semana,
                    "key": key
                })
                semanas_selecionadas_lista.append(key)
        if not semanas_filtradas:
            semanas_filtradas = semanas
    else:
        semanas_filtradas = semanas
    
    semanas_filtradas.sort(key=lambda x: (ordem_periodos.index(x["periodo"]) if x["periodo"] in ordem_periodos else 999, x["semana"]))
    
    periodos_disponiveis = []
    for periodo in set(s[0] for s in semanas_set):
        semanas_periodo = sorted([s[1] for s in semanas_set if s[0] == periodo])
        registros_por_semana = {}
        for semana in semanas_periodo:
            count = sum(1 for r in registros if r["periodo"] == periodo and r["semana"] == semana)
            registros_por_semana[semana] = count
        
        periodos_disponiveis.append({
            "periodo": periodo,
            "semanas": semanas_periodo,
            "registros_por_semana": registros_por_semana
        })
    
    periodos_disponiveis.sort(key=lambda x: ordem_periodos.index(x["periodo"]) if x["periodo"] in ordem_periodos else 999)
    
    return render_template("visualizar_tabela.html",
                         treinos=treinos,
                         treino_selecionado=treino_selecionado,
                         musculos=musculos,
                         musculo_selecionado=musculo_selecionado,
                         ordenar=ordenar,
                         exercicios=exercicios_filtrados,
                         semanas=semanas_filtradas,
                         registros_por_exercicio=registros_por_exercicio,
                         semanas_selecionadas=semanas_filtro,
                         semanas_selecionadas_lista=semanas_selecionadas_lista,
                         periodos_disponiveis=periodos_disponiveis)