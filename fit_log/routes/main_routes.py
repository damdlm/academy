from flask import Blueprint, render_template
from utils import load_json

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    treinos = load_json("treinos.json")
    registros = load_json("registros.json")
    
    total_registros = len(registros)
    semanas_treinadas = len(set((r["periodo"], r["semana"]) for r in registros))
    
    ultima_semana = "N/A"
    if registros:
        ultimo = registros[-1]
        ultima_semana = f"{ultimo['periodo']} - Semana {ultimo['semana']}"
    
    return render_template("index.html", 
                         treinos=treinos,
                         total_registros=total_registros,
                         semanas_treinadas=semanas_treinadas,
                         ultima_semana=ultima_semana)