from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    load_json, save_json, get_versoes_globais, get_versao_ativa,
    get_treinos_da_versao, get_exercicios_do_treino,
    adicionar_treino_na_versao, editar_treino_na_versao as editar_treino_utils, 
    remover_treino_da_versao,
    migrar_versoes_para_novo_formato, verificar_exercicio_em_versoes,
    adicionar_exercicio_ao_treino, remover_exercicio_do_treino,
    data_atual_iso, formatar_data, data_atual_formatada
)

version_bp = Blueprint('version', __name__)

@version_bp.route("/gerenciar/versoes-global")
def gerenciar_versoes_global():
    """Página principal para gerenciar versões globais"""
    versoes = get_versoes_globais()
    
    # Separar versões atuais e antigas
    versoes_atuais = [v for v in versoes if v.get("data_fim") is None]
    versoes_antigas = [v for v in versoes if v.get("data_fim") is not None]
    
    # Ordenar versões antigas pela data de início (mais recente primeiro)
    versoes_antigas.sort(key=lambda x: x.get('data_inicio', '1900-01-01'), reverse=True)
    
    # Combinar: atuais primeiro, depois antigas ordenadas
    versoes = versoes_atuais + versoes_antigas
    
    # Formatar as datas para exibição
    for v in versoes:
        v['data_inicio_formatada'] = formatar_data(v.get('data_inicio'))
        v['data_fim_formatada'] = formatar_data(v.get('data_fim'))
    
    exercicios = load_json("exercicios.json")
    treinos = load_json("treinos.json")
    musculos = sorted(set(e["musculo"] for e in exercicios))
    
    now = datetime.now
    
    return render_template("gerenciar_versoes_global.html",
                         versoes=versoes,
                         exercicios=exercicios,
                         treinos=treinos,
                         musculos=musculos,
                         now=now,
                         data_atual_iso=data_atual_iso,
                         data_atual_formatada=data_atual_formatada)

@version_bp.route("/versao/<int:versao_id>", methods=["GET", "POST"])
def ver_versao(versao_id):
    """Visualiza e edita detalhes de uma versão específica com seus treinos"""
    versoes = get_versoes_globais()
    versao = next((v for v in versoes if v["id"] == versao_id), None)
    
    if not versao:
        flash("Versão não encontrada!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    # Processar o POST do formulário de edição da versão
    if request.method == "POST":
        versao["descricao"] = request.form["descricao"]
        versao["data_inicio"] = request.form["data_inicio"]
        versao["data_fim"] = request.form.get("data_fim") or None
        
        save_json("versoes_treino.json", versoes)
        flash(f"Versão {versao['versao']} atualizada com sucesso!", "success")
        return redirect(url_for("version.ver_versao", versao_id=versao_id))
    
    # Formatar datas para exibição
    versao['data_inicio_formatada'] = formatar_data(versao.get('data_inicio'))
    versao['data_fim_formatada'] = formatar_data(versao.get('data_fim'))
    
    exercicios = load_json("exercicios.json")
    treinos = load_json("treinos.json")
    musculos = sorted(set(e["musculo"] for e in exercicios))
    
    return render_template("ver_versao.html",
                         versao=versao,
                         exercicios=exercicios,
                         treinos=treinos,
                         musculos=musculos,
                         data_atual_iso=data_atual_iso)

@version_bp.route("/versao/<int:versao_id>/treino/novo", methods=["GET", "POST"])
def novo_treino_na_versao(versao_id):
    """Adiciona um novo treino em uma versão, podendo carregar um treino padrão"""
    versoes = get_versoes_globais()
    versao = next((v for v in versoes if v["id"] == versao_id), None)
    
    if not versao:
        flash("Versão não encontrada!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    # Formatar datas para exibição
    versao['data_inicio_formatada'] = formatar_data(versao.get('data_inicio'))
    versao['data_fim_formatada'] = formatar_data(versao.get('data_fim'))
    
    if request.method == "POST":
        treino_id = request.form["treino_id"].upper()
        nome_treino = request.form["nome_treino"]
        descricao_treino = request.form["descricao_treino"]
        tipo_criacao = request.form.get("tipo_criacao", "vazio")
        
        exercicios_ids = []
        
        if tipo_criacao == "padrao":
            treino_padrao_id = request.form.get("treino_padrao")
            if treino_padrao_id:
                treinos_padrao = load_json("treinos.json")
                treino_padrao = next((t for t in treinos_padrao if t["id"] == treino_padrao_id), None)
                
                if treino_padrao:
                    todos_exercicios = load_json("exercicios.json")
                    exercicios_ids = [
                        ex["id"] for ex in todos_exercicios 
                        if ex.get("treino") == treino_padrao_id
                    ]
        
        if adicionar_treino_na_versao(versao_id, treino_id, nome_treino, descricao_treino, exercicios_ids):
            flash(f"Treino {treino_id} adicionado à versão {versao['versao']}!", "success")
        else:
            flash("Erro ao adicionar treino!", "danger")
        
        return redirect(url_for("version.ver_versao", versao_id=versao_id))
    
    treinos_padrao = load_json("treinos.json")
    exercicios = load_json("exercicios.json")
    
    return render_template("novo_treino_versao.html",
                         versao=versao,
                         treinos_padrao=treinos_padrao,
                         exercicios=exercicios,
                         data_atual_iso=data_atual_iso)

@version_bp.route("/versao/<int:versao_id>/treino/<treino_id>/editar", methods=["GET", "POST"])
def editar_treino_na_versao(versao_id, treino_id):
    """Edita um treino existente em uma versão"""
    versoes = get_versoes_globais()
    versao = next((v for v in versoes if v["id"] == versao_id), None)
    
    if not versao or 'treinos' not in versao:
        flash("Versão ou treino não encontrado!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    treino = versao['treinos'].get(treino_id)
    if not treino:
        flash("Treino não encontrado!", "danger")
        return redirect(url_for("version.ver_versao", versao_id=versao_id))
    
    # Formatar datas para exibição
    versao['data_inicio_formatada'] = formatar_data(versao.get('data_inicio'))
    versao['data_fim_formatada'] = formatar_data(versao.get('data_fim'))
    
    if request.method == "POST":
        nome_treino = request.form["nome_treino"]
        descricao_treino = request.form["descricao_treino"]
        
        exercicios_ids = request.form.getlist("exercicios[]")
        exercicios_ids = [int(id) for id in exercicios_ids]
        
        if editar_treino_utils(versao_id, treino_id, nome_treino, descricao_treino, exercicios_ids):
            flash(f"Treino {treino_id} atualizado!", "success")
        else:
            flash("Erro ao atualizar treino!", "danger")
        
        return redirect(url_for("version.ver_versao", versao_id=versao_id))
    
    exercicios = load_json("exercicios.json")
    musculos = sorted(set(e["musculo"] for e in exercicios))
    
    return render_template("editar_treino_versao.html",
                         versao=versao,
                         treino_id=treino_id,
                         treino=treino,
                         exercicios=exercicios,
                         musculos=musculos)

@version_bp.route("/versao/<int:versao_id>/treino/<treino_id>/excluir")
def excluir_treino_da_versao(versao_id, treino_id):
    """Exclui um treino de uma versão"""
    if remover_treino_da_versao(versao_id, treino_id):
        flash(f"Treino {treino_id} removido da versão!", "success")
    else:
        flash("Erro ao remover treino!", "danger")
    
    return redirect(url_for("version.ver_versao", versao_id=versao_id))

@version_bp.route("/versao/<int:versao_id>/treino/<treino_id>/exercicio/adicionar", methods=["POST"])
def adicionar_exercicio_ao_treino_route(versao_id, treino_id):
    """Adiciona um exercício existente a um treino da versão"""
    data = request.get_json()
    exercicio_id = data.get("exercicio_id")
    
    if not exercicio_id:
        return jsonify({"success": False, "error": "ID do exercício não fornecido"}), 400
    
    if adicionar_exercicio_ao_treino(versao_id, treino_id, exercicio_id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Erro ao adicionar exercício"}), 400

@version_bp.route("/versao/<int:versao_id>/treino/<treino_id>/exercicio/<int:exercicio_id>/remover", methods=["POST"])
def remover_exercicio_do_treino_route(versao_id, treino_id, exercicio_id):
    """Remove um exercício de um treino da versão"""
    if remover_exercicio_do_treino(versao_id, treino_id, exercicio_id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Erro ao remover exercício"}), 400

@version_bp.route("/versao/<int:versao_id>/treino/<treino_id>/reordenar", methods=["POST"])
def reordenar_exercicios_route(versao_id, treino_id):
    """Reordena os exercícios de um treino"""
    from utils import reordenar_exercicios_do_treino
    data = request.get_json()
    nova_ordem = data.get("nova_ordem")
    
    if reordenar_exercicios_do_treino(versao_id, treino_id, nova_ordem):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 400

@version_bp.route("/migrar/versoes")
def migrar_versoes():
    """Rota para migrar versões antigas para o novo formato"""
    try:
        versoes_migradas = migrar_versoes_para_novo_formato()
        save_json("versoes_treino.json", versoes_migradas)
        flash(f"✅ Versões migradas com sucesso para o novo formato!", "success")
    except Exception as e:
        flash(f"Erro durante a migração: {str(e)}", "danger")
        print(f"Erro na migração: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/salvar/versao-global", methods=["POST"])
def salvar_versao_global():
    """Cria uma nova versão global"""
    versoes = load_json("versoes_treino.json")
    
    descricao = request.form["descricao"]
    data_inicio = request.form["data_inicio"]
    data_fim = request.form.get("data_fim") or None
    
    versao_ativa = next((v for v in versoes if v.get("data_fim") is None), None)
    
    if versao_ativa and not data_fim:
        flash(f"Já existe uma versão ativa (Versão {versao_ativa['versao']}). Finalize-a antes de criar uma nova.", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    if versoes:
        novo_id = max([v["id"] for v in versoes]) + 1
        nova_versao_num = max([v["versao"] for v in versoes]) + 1
    else:
        novo_id = 1
        nova_versao_num = 1
    
    for v in versoes:
        if v.get("data_fim") is None:
            v["data_fim"] = data_inicio
    
    nova_versao = {
        "id": novo_id,
        "versao": nova_versao_num,
        "descricao": descricao,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "treinos": {}
    }
    
    versoes.append(nova_versao)
    save_json("versoes_treino.json", versoes)
    
    flash(f"Nova versão global criada com sucesso!", "success")
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/finalizar/versao-global/<int:versao_id>")
def finalizar_versao_global(versao_id):
    """Finaliza uma versão global"""
    versoes = load_json("versoes_treino.json")
    
    versao = next((v for v in versoes if v.get("id") == versao_id), None)
    if not versao:
        flash("Versão não encontrada!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    if versao.get("data_fim"):
        flash(f"Versão {versao['versao']} já foi finalizada em {formatar_data(versao['data_fim'])}.", "warning")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    data_atual = datetime.now().strftime("%Y-%m-%d")
    
    versao["data_fim"] = data_atual
    save_json("versoes_treino.json", versoes)
    
    flash(f"Versão {versao['versao']} finalizada com sucesso em {formatar_data(data_atual)}!", "success")
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/clonar/versao-global/<int:versao_id>")
def clonar_versao_global(versao_id):
    """Clona uma versão existente para criar uma nova"""
    versoes = load_json("versoes_treino.json")
    
    versao_origem = next((v for v in versoes if v.get("id") == versao_id), None)
    if not versao_origem:
        flash("Versão não encontrada!", "danger")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    data_atual = datetime.now().strftime("%Y-%m-%d")
    
    versao_ativa = next((v for v in versoes if v.get("data_fim") is None), None)
    if versao_ativa:
        flash(f"Já existe uma versão ativa (Versão {versao_ativa['versao']}). Finalize-a antes de clonar.", "warning")
        return redirect(url_for("version.gerenciar_versoes_global"))
    
    novo_id = max([v["id"] for v in versoes]) + 1
    nova_versao_num = max([v["versao"] for v in versoes]) + 1
    
    treinos_clonados = {}
    for treino_id, treino_data in versao_origem.get("treinos", {}).items():
        treinos_clonados[treino_id] = {
            "nome": treino_data.get("nome", f"Treino {treino_id}"),
            "descricao": treino_data.get("descricao", ""),
            "exercicios": treino_data.get("exercicios", []).copy()
        }
    
    nova_versao = {
        "id": novo_id,
        "versao": nova_versao_num,
        "descricao": f"Cópia de {versao_origem['descricao']}",
        "data_inicio": data_atual,
        "data_fim": None,
        "treinos": treinos_clonados
    }
    
    versoes.append(nova_versao)
    save_json("versoes_treino.json", versoes)
    
    flash(f"✅ Versão {nova_versao_num} criada a partir da versão {versao_origem['versao']}!", "success")
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/gerenciar/versoes/<treino_id>")
def gerenciar_versoes(treino_id):
    """Redireciona para versões globais"""
    flash("As versões agora são globais. Gerenciando todas as versões...", "info")
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/salvar/versao", methods=["POST"])
def salvar_versao():
    """Redireciona para salvar versão global"""
    return redirect(url_for("version.salvar_versao_global"))

@version_bp.route("/editar/versao", methods=["POST"])
def editar_versao():
    """Redireciona para editar versão global"""
    return redirect(url_for("version.gerenciar_versoes_global"))

@version_bp.route("/finalizar/versao", methods=["POST"])
def finalizar_versao():
    """Redireciona para finalizar versão global"""
    return redirect(url_for("version.gerenciar_versoes_global"))