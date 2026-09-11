from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.livro import LivroModel
from src.models.avaliacao import AvaliacaoModel
from src.models.aluno import AlunoModel
from src.config import TEMAS_LIVROS
from src.services.book_fetcher import buscar_metadados_online, SUGESTOES_RAPIDAS
from src.routes.auth_routes import login_required, roles_required

book_bp = Blueprint("books", __name__)

@book_bp.route("/")
def dashboard():
    """Painel inicial: Portal de Consulta delimitado no topo e Obras em Destaque abaixo."""
    if "user_id" not in session:
        return redirect(url_for("auth.login_view"))
    stats = LivroModel.estatisticas()
    livros_destaque = LivroModel.listar()[:6]
    return render_template("dashboard.html", stats=stats, livros_destaque=livros_destaque, temas=TEMAS_LIVROS)

@book_bp.route("/livros")
def listar_livros():
    """
    Portal de Consulta ao Acervo: catálogo completo com filtragem por temas
    e busca com exibição das capas dos livros ao lado dos títulos.
    """
    tema_selecionado = request.args.get("tema", "Todos")
    termo_busca = request.args.get("busca", "").strip()

    livros = LivroModel.listar(tema=tema_selecionado, busca=termo_busca)

    return render_template(
        "livros/index.html",
        livros=livros,
        temas=TEMAS_LIVROS,
        tema_ativo=tema_selecionado,
        busca=termo_busca
    )

@book_bp.route("/livros/<int:livro_id>")
def detalhes_livro(livro_id):
    """Exibe capa e detalhes completos da obra, avaliações e botão de empréstimo."""
    livro = LivroModel.buscar_por_id(livro_id)
    if not livro:
        flash("Livro não encontrado no acervo.", "erro")
        return redirect(url_for("books.listar_livros"))

    avaliacoes = AvaliacaoModel.listar_por_livro(livro_id)
    stats_aval = AvaliacaoModel.calcular_estatisticas_livro(livro_id)
    alunos = AlunoModel.listar() if session.get("user_tipo") in ["admin", "bibliotecario"] else []

    return render_template(
        "livros/detalhes.html",
        livro=livro,
        avaliacoes=avaliacoes,
        stats_aval=stats_aval,
        alunos=alunos
    )

@book_bp.route("/livros/<int:livro_id>/avaliar", methods=["POST"])
@login_required
def avaliar_livro(livro_id):
    """Permite ao Aluno avaliar o livro com nota de 1 a 5 estrelas e comentário."""
    nota = request.form.get("nota", "5")
    comentario = request.form.get("comentario", "").strip()
    aluno_nome = session.get("user_nome", "Aluno UniEnsino")
    aluno_id = session.get("aluno_id")

    res = AvaliacaoModel.adicionar(
        livro_id=livro_id,
        aluno_id=aluno_id,
        aluno_nome=aluno_nome,
        nota=nota,
        comentario=comentario
    )

    if res.get("sucesso"):
        flash("Sua avaliação foi registrada com sucesso! Obrigado por colaborar com o UniBook.", "sucesso")
    else:
        flash(f"Erro ao registrar avaliação: {res.get('erro')}", "erro")

    return redirect(url_for("books.detalhes_livro", livro_id=livro_id))

@book_bp.route("/livros/novo", methods=["GET", "POST"])
@login_required
@roles_required("admin", "bibliotecario")
def adicionar_livro():
    """
    Cadastro Prático de Livros:
    - Busca automática online por título ou ISBN
    - Sugestões express em 1 clique
    - Formulário padrão pré-preenchível com capa
    """
    busca_online = request.args.get("busca_online", "").strip()
    resultados_online = []
    if busca_online:
        resultados_online = buscar_metadados_online(busca_online)
        if not resultados_online:
            flash(f"Nenhum livro localizado na base aberta para '{busca_online}'.", "aviso")

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        tema = request.form.get("tema", "").strip()
        ano_str = request.form.get("ano", "").strip()
        qtd_str = request.form.get("quantidade", "1").strip()
        sinopse = request.form.get("sinopse", "").strip()
        capa_url = request.form.get("capa_url", "").strip()

        if not titulo or not autor or not tema:
            flash("Título, autor e tema são obrigatórios.", "erro")
            return render_template("livros/novo.html", temas=TEMAS_LIVROS, sugestoes=SUGESTOES_RAPIDAS, resultados_online=resultados_online)

        ano = int(ano_str) if ano_str.isdigit() else None
        quantidade = int(qtd_str) if qtd_str.isdigit() and int(qtd_str) > 0 else 1

        res = LivroModel.adicionar(
            titulo=titulo,
            autor=autor,
            tema=tema,
            ano=ano,
            quantidade=quantidade,
            sinopse=sinopse,
            capa_url=capa_url
        )

        if res.get("sucesso"):
            flash(f"Livro '{titulo}' cadastrado no tema '{tema}' com sucesso!", "sucesso")
            return redirect(url_for("books.listar_livros", tema=tema))
        else:
            flash(f"Erro ao cadastrar livro: {res.get('erro')}", "erro")

    return render_template(
        "livros/novo.html", 
        temas=TEMAS_LIVROS, 
        sugestoes=SUGESTOES_RAPIDAS,
        resultados_online=resultados_online,
        busca_online=busca_online
    )

@book_bp.route("/livros/adicionar-rapido", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def adicionar_rapido():
    """Adiciona uma obra imediatamente ao acervo com capa e metadados com apenas 1 clique."""
    titulo = request.form.get("titulo", "").strip()
    autor = request.form.get("autor", "").strip()
    tema = request.form.get("tema", "Acadêmico/Técnico").strip()
    ano_str = request.form.get("ano", "").strip()
    quantidade_str = request.form.get("quantidade", "3").strip()
    sinopse = request.form.get("sinopse", "").strip()
    capa_url = request.form.get("capa_url", "").strip()

    ano = int(ano_str) if ano_str.isdigit() else None
    quantidade = int(quantidade_str) if quantidade_str.isdigit() else 3

    res = LivroModel.adicionar(
        titulo=titulo,
        autor=autor,
        tema=tema,
        ano=ano,
        quantidade=quantidade,
        sinopse=sinopse,
        capa_url=capa_url
    )

    if res.get("sucesso"):
        flash(f"✨ Obra '{titulo}' adicionada ao acervo em 1 clique!", "sucesso")
    else:
        flash(f"Erro ao adicionar: {res.get('erro')}", "erro")

    return redirect(url_for("books.listar_livros", tema=tema))

@book_bp.route("/livros/<int:livro_id>/excluir", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def excluir_livro(livro_id):
    """Exclui livro do acervo (exclusivo para Bibliotecário e Administrador; Aluno bloqueado)."""
    livro = LivroModel.buscar_por_id(livro_id)
    if not livro:
        flash("Livro não encontrado.", "erro")
        return redirect(url_for("books.listar_livros"))

    sucesso = LivroModel.excluir(livro_id)
    if sucesso:
        flash(f"Livro '{livro['titulo']}' excluído do acervo.", "sucesso")
    else:
        flash("Não foi possível excluir o livro.", "erro")

    return redirect(url_for("books.listar_livros"))
