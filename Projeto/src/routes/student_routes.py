from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models.aluno import AlunoModel
from src.config import CURSOS_UNIENSINO
from src.routes.auth_routes import login_required, roles_required

student_bp = Blueprint("students", __name__)

@student_bp.route("/alunos")
@login_required
@roles_required("admin", "bibliotecario")
def listar_alunos():
    """Listagem de todos os alunos da UniEnsino (apenas Administrador e Bibliotecário)."""
    busca = request.args.get("busca", "").strip()
    alunos = AlunoModel.listar(busca=busca)
    return render_template("alunos/index.html", alunos=alunos, busca=busca, cursos=CURSOS_UNIENSINO)

@student_bp.route("/alunos/novo", methods=["GET", "POST"])
@login_required
@roles_required("admin", "bibliotecario")
def cadastrar_aluno():
    """Formulário e processamento para cadastro de novos alunos."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        matricula = request.form.get("matricula", "").strip()
        curso = request.form.get("curso", "").strip()
        email = request.form.get("email", "").strip()

        if not nome or not matricula or not curso:
            flash("Nome, matrícula (RA) e curso são obrigatórios.", "erro")
            return render_template("alunos/novo.html", cursos=CURSOS_UNIENSINO)

        if not email:
            primeiro_nome = nome.split()[0].lower()
            sobrenome = nome.split()[-1].lower() if len(nome.split()) > 1 else "aluno"
            email = f"{primeiro_nome}.{sobrenome}@uniensino.edu.br"

        res = AlunoModel.cadastrar(nome, matricula, curso, email)
        if res.get("sucesso"):
            flash(f"Aluno(a) '{nome}' (RA: {matricula}) matriculado(a) com sucesso!", "sucesso")
            return redirect(url_for("students.listar_alunos"))
        else:
            erro_msg = res.get("erro", "")
            if "UNIQUE" in erro_msg:
                flash(f"Já existe um aluno cadastrado com o RA '{matricula}'.", "erro")
            else:
                flash(f"Erro ao cadastrar aluno: {erro_msg}", "erro")

    return render_template("alunos/novo.html", cursos=CURSOS_UNIENSINO)

@student_bp.route("/alunos/<int:aluno_id>/editar", methods=["POST"])
@login_required
@roles_required("admin", "bibliotecario")
def editar_aluno(aluno_id):
    """
    Edição de dados do aluno.
    REGRA DO TRABALHO: O Bibliotecário NÃO pode alterar o e-mail institucional sem autorização!
    """
    nome = request.form.get("nome", "").strip()
    matricula = request.form.get("matricula", "").strip()
    curso = request.form.get("curso", "").strip()
    email = request.form.get("email", "").strip()
    usuario_tipo = session.get("user_tipo", "aluno")

    res = AlunoModel.atualizar(
        aluno_id=aluno_id,
        nome=nome,
        matricula=matricula,
        curso=curso,
        email=email,
        usuario_tipo=usuario_tipo
    )

    if res.get("sucesso"):
        flash("Dados do aluno atualizados com sucesso.", "sucesso")
    else:
        flash(res.get("erro"), "erro")

    return redirect(url_for("students.listar_alunos"))

@student_bp.route("/alunos/<int:aluno_id>/excluir", methods=["POST"])
@login_required
@roles_required("admin")
def excluir_aluno(aluno_id):
    """Exclui aluno do sistema (exclusivo do Administrador; Aluno e Bibliotecário bloqueados)."""
    aluno = AlunoModel.buscar_por_id(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "erro")
        return redirect(url_for("students.listar_alunos"))

    sucesso = AlunoModel.excluir(aluno_id)
    if sucesso:
        flash(f"Aluno(a) '{aluno['nome']}' (RA: {aluno['matricula']}) excluído(a) com sucesso.", "sucesso")
    else:
        flash("Não foi possível excluir o aluno.", "erro")

    return redirect(url_for("students.listar_alunos"))
