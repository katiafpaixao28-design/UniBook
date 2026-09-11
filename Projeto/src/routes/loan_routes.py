from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.emprestimo import EmprestimoModel
from src.models.aluno import AlunoModel
from src.models.livro import LivroModel
from src.routes.auth_routes import login_required, roles_required

loan_bp = Blueprint("loans", __name__)

@loan_bp.route("/emprestimos")
@login_required
@roles_required("admin", "bibliotecario")
def listar_todos():
    """Painel de gestão de todos os empréstimos (Bibliotecário e Administrador)."""
    status_filtro = request.args.get("status", "todos")
    emprestimos = EmprestimoModel.listar_todos(status_filtro=status_filtro)
    return render_template("emprestimos/index.html", emprestimos=emprestimos, status_ativo=status_filtro)

@loan_bp.route("/emprestimos/meus")
@login_required
def meus_emprestimos():
    """Área exclusiva do Aluno para consultar seus próprios livros emprestados."""
    aluno_id = session.get("aluno_id")
    if not aluno_id:
        # Se for admin ou bibliotecário navegando aqui, busca pelo primeiro aluno ou redireciona
        if session.get("user_tipo") in ["admin", "bibliotecario"]:
            return redirect(url_for("loans.listar_todos"))
        flash("Sua conta de usuário não possui um cadastro de aluno vinculado.", "aviso")
        return redirect(url_for("books.listar_livros"))

    emprestimos = EmprestimoModel.listar_por_aluno(aluno_id)
    return render_template("emprestimos/meus.html", emprestimos=emprestimos)

@loan_bp.route("/emprestimos/solicitar/<int:livro_id>", methods=["POST"])
@login_required
def pegar_emprestado(livro_id):
    """
    Permite ao Aluno realizar o empréstimo de um livro para si mesmo,
    ou ao Bibliotecário/Admin registrar para um aluno selecionado.
    """
    user_tipo = session.get("user_tipo")
    aluno_id = session.get("aluno_id")

    # Se for bibliotecário ou admin, pode selecionar qual aluno vai retirar
    if user_tipo in ["admin", "bibliotecario"]:
        aluno_selecionado = request.form.get("aluno_id")
        if aluno_selecionado:
            aluno_id = int(aluno_selecionado)
        elif not aluno_id:
            flash("Selecione um aluno para registrar o empréstimo.", "aviso")
            return redirect(url_for("books.detalhes_livro", livro_id=livro_id))

    if not aluno_id:
        flash("Não foi possível identificar o aluno para o empréstimo.", "erro")
        return redirect(url_for("books.detalhes_livro", livro_id=livro_id))

    res = EmprestimoModel.emprestar(livro_id=livro_id, aluno_id=aluno_id)
    if res.get("sucesso"):
        flash(f"Empréstimo registrado com sucesso! Devolução prevista até: {res.get('data_prevista')}.", "sucesso")
        if user_tipo == "aluno":
            return redirect(url_for("loans.meus_emprestimos"))
        return redirect(url_for("loans.listar_todos"))
    else:
        flash(f"Não foi possível realizar o empréstimo: {res.get('erro')}", "erro")
        return redirect(url_for("books.detalhes_livro", livro_id=livro_id))

@loan_bp.route("/emprestimos/<int:emp_id>/renovar", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def renovar(emp_id):
    """
    Renovação de livro (+7 dias).
    Permitido apenas para Bibliotecário e Administrador.
    """
    res = EmprestimoModel.renovar(emp_id, dias_adicionais=7)
    if res.get("sucesso"):
        flash(f"Empréstimo renovado com sucesso! Nova data de entrega: {res.get('nova_data')}.", "sucesso")
    else:
        flash(f"Erro ao renovar: {res.get('erro')}", "erro")
    return redirect(url_for("loans.listar_todos"))

@loan_bp.route("/emprestimos/<int:emp_id>/devolver", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def devolver(emp_id):
    """Devolução de exemplar de livro à biblioteca."""
    res = EmprestimoModel.devolver(emp_id)
    if res.get("sucesso"):
        flash("Livro devolvido com sucesso ao acervo!", "sucesso")
    else:
        flash(f"Erro ao devolver: {res.get('erro')}", "erro")
    return redirect(url_for("loans.listar_todos"))

@loan_bp.route("/emprestimos/<int:emp_id>/multa", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def aplicar_multa(emp_id):
    """
    Aplicação de multa por atraso ou avaria.
    Permitido para Bibliotecário e Administrador.
    """
    valor = request.form.get("valor", "5.00").replace(",", ".")
    motivo = request.form.get("motivo", "Atraso na devolução do livro")
    res = EmprestimoModel.aplicar_multa(emp_id, valor, motivo)
    if res.get("sucesso"):
        flash(f"Multa de R$ {float(valor):.2f} aplicada com sucesso ao empréstimo!", "sucesso")
    else:
        flash(f"Erro ao aplicar multa: {res.get('erro')}", "erro")
    return redirect(url_for("loans.listar_todos"))

@loan_bp.route("/emprestimos/<int:emp_id>/quitar-multa", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def quitar_multa(emp_id):
    """Marca multa como quitada/paga."""
    EmprestimoModel.quitar_multa(emp_id)
    flash("Multa quitada com sucesso!", "sucesso")
    return redirect(url_for("loans.listar_todos"))
