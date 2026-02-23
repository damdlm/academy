from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import load_json, save_json, clear_cache, buscar_musculo_no_catalogo, get_series_from_registro, verificar_exercicio_em_versoes

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/gerenciar")
def gerenciar():
    treinos = load_json("treinos.json")
    exercicios = load_json("exercicios.json")
    registros = load_json("registros.json")
    
    musculos = sorted(set(e["musculo"] for e in exercicios))
    
    exercicios_por_treino = {}
    for ex in exercicios:
        treino_id = ex["treino"]
        if treino_id not in exercicios_por_treino:
            exercicios_por_treino[treino_id] = 0
        exercicios_por_treino[treino_id] += 1
    
    ultimas_cargas = {}
    for ex in exercicios:
        registros_ex = [r for r in registros if r["exercicio_id"] == ex["id"]]
        if registros_ex:
            ultimo_registro = registros_ex[-1]
            series = get_series_from_registro(ultimo_registro)
            if series:
                ultimas_cargas[ex["id"]] = series[0]["carga"]
    
    return render_template("gerenciar_treinos.html",
                         treinos=treinos,
                         exercicios=exercicios,
                         musculos=musculos,
                         exercicios_por_treino=exercicios_por_treino,
                         ultimas_cargas=ultimas_cargas)

@admin_bp.route("/salvar/treino", methods=["POST"])
def salvar_treino():
    treinos = load_json("treinos.json")
    
    novo_treino = {
        "id": request.form["id"].upper(),
        "descricao": request.form["descricao"]
    }
    
    if any(t["id"] == novo_treino["id"] for t in treinos):
        flash(f"Treino {novo_treino['id']} já existe!", "danger")
    else:
        treinos.append(novo_treino)
        treinos.sort(key=lambda x: x["id"])
        save_json("treinos.json", treinos)
        
        flash(f"Treino {novo_treino['id']} criado com sucesso!", "success")
    
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/editar/treino", methods=["POST"])
def editar_treino():
    treinos = load_json("treinos.json")
    
    treino_id_original = request.form["id_original"]
    novo_id = request.form["id"].upper()
    nova_descricao = request.form["descricao"]
    
    if novo_id != treino_id_original and any(t["id"] == novo_id for t in treinos):
        flash(f"Treino {novo_id} já existe!", "danger")
        return redirect(url_for("admin.gerenciar"))
    
    for treino in treinos:
        if treino["id"] == treino_id_original:
            treino["id"] = novo_id
            treino["descricao"] = nova_descricao
            break
    
    exercicios = load_json("exercicios.json")
    for ex in exercicios:
        if ex["treino"] == treino_id_original:
            ex["treino"] = novo_id
    
    save_json("treinos.json", treinos)
    save_json("exercicios.json", exercicios)
    
    flash(f"Treino {treino_id_original} atualizado para {novo_id} com sucesso!", "success")
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/salvar/exercicio", methods=["POST"])
def salvar_exercicio():
    exercicios = load_json("exercicios.json")
    
    novo_id = max([e["id"] for e in exercicios], default=0) + 1
    
    nome_exercicio = request.form["nome"]
    musculo = request.form["musculo"]
    treino = request.form["treino"]
    
    musculo_final = None

    if musculo and musculo.strip() != "":
        musculo_final = musculo
    
    if musculo_final is None:
        musculo_encontrado = buscar_musculo_no_catalogo(nome_exercicio)
        if musculo_encontrado:
            musculo_final = musculo_encontrado
            flash(f"Músculo '{musculo_final}' encontrado automaticamente no catálogo!", "info")
    
    if musculo_final is None:
        musculo_final = "Outros"
        flash("Músculo não encontrado no catálogo. Usando 'Outros'.", "warning")

    novo_exercicio = {
        "id": novo_id,
        "nome": nome_exercicio,
        "musculo": musculo_final,
        "treino": treino
    }
    
    exercicios.append(novo_exercicio)
    exercicios.sort(key=lambda x: x["nome"])
    save_json("exercicios.json", exercicios)
    
    flash(f"Exercício '{novo_exercicio['nome']}' criado com sucesso!", "success")
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/editar/exercicio", methods=["POST"])
def editar_exercicio():
    exercicios = load_json("exercicios.json")
    
    exercicio_id = int(request.form["id"])
    nome_exercicio = request.form["nome"]
    musculo = request.form["musculo"]
    treino = request.form["treino"]
    
    if not musculo or musculo == "":
        musculo_encontrado = buscar_musculo_no_catalogo(nome_exercicio)
        if musculo_encontrado:
            musculo = musculo_encontrado
            flash(f"Músculo atualizado para '{musculo}' com base no catálogo!", "info")
        else:
            exercicio_original = next((e for e in exercicios if e["id"] == exercicio_id), None)
            if exercicio_original:
                musculo = exercicio_original["musculo"]
            else:
                musculo = "Outros"
    
    for ex in exercicios:
        if ex["id"] == exercicio_id:
            ex["nome"] = nome_exercicio
            ex["musculo"] = musculo
            ex["treino"] = treino
            break
    
    save_json("exercicios.json", exercicios)
    flash("Exercício atualizado com sucesso!", "success")
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/excluir/treino/<treino_id>")
def excluir_treino(treino_id):
    treinos = load_json("treinos.json")
    exercicios = load_json("exercicios.json")
    registros = load_json("registros.json")
    
    treinos = [t for t in treinos if t["id"] != treino_id]
    
    exercicios_treino = [e for e in exercicios if e["treino"] == treino_id]
    ids_exercicios = [e["id"] for e in exercicios_treino]
    
    exercicios = [e for e in exercicios if e["treino"] != treino_id]
    registros = [r for r in registros if r["exercicio_id"] not in ids_exercicios]
    
    save_json("treinos.json", treinos)
    save_json("exercicios.json", exercicios)
    save_json("registros.json", registros)
    
    clear_cache()
    flash(f"Treino {treino_id} e todos os seus dados foram excluídos!", "success")
    return redirect(url_for("admin.gerenciar"))

@admin_bp.route("/excluir/exercicio/<int:exercicio_id>")
def excluir_exercicio(exercicio_id):
    exercicios = load_json("exercicios.json")
    registros = load_json("registros.json")
    
    exercicio = next((e for e in exercicios if e["id"] == exercicio_id), None)
    nome = exercicio["nome"] if exercicio else "Exercício"
    
    exercicios = [e for e in exercicios if e["id"] != exercicio_id]
    registros = [r for r in registros if r["exercicio_id"] != exercicio_id]
    
    save_json("exercicios.json", exercicios)
    save_json("registros.json", registros)
    
    clear_cache()
    flash(f"'{nome}' e todos os seus registros foram excluídos!", "success")
    return redirect(url_for("admin.gerenciar"))

# ===== NOVA ROTA PARA DETALHES DO EXERCÍCIO =====
@admin_bp.route("/exercicio/detalhes/<int:exercicio_id>")
def exercicio_detalhes(exercicio_id):
    """Mostra detalhes de um exercício, incluindo em quais versões aparece"""
    from utils import verificar_exercicio_em_versoes
    
    exercicios = load_json("exercicios.json")
    exercicio = next((e for e in exercicios if e["id"] == exercicio_id), None)
    
    if not exercicio:
        flash("Exercício não encontrado!", "danger")
        return redirect(url_for("admin.gerenciar"))
    
    versoes = verificar_exercicio_em_versoes(exercicio_id)
    
    return render_template("exercicio_detalhes.html",
                         exercicio=exercicio,
                         versoes=versoes)