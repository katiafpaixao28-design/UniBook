from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.models.usuario import UsuarioModel

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    """Decorador para proteger rotas que exigem usuário autenticado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, faça login para acessar esta funcionalidade.", "aviso")
            return redirect(url_for("auth.login_view"))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    """Decorador em Python puro para controle de acesso baseado em papéis (RBAC)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Por favor, faça login para continuar.", "aviso")
                return redirect(url_for("auth.login_view"))
            user_tipo = session.get("user_tipo")
            if user_tipo not in allowed_roles:
                flash(f"Acesso não permitido: seu perfil ({user_tipo}) não tem permissão para realizar esta operação.", "erro")
                return redirect(url_for("books.listar_livros"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route("/login", methods=["GET", "POST"])
def login_view():
    """Tela de login e processamento de credenciais."""
    if "user_id" in session:
        return redirect(url_for("books.listar_livros"))

    if request.method == "POST":
        identificador = request.form.get("identificador", "").strip()
        senha = request.form.get("senha", "").strip()

        if not identificador or not senha:
            flash("Informe seu e-mail ou RA e a senha.", "erro")
            return render_template("login.html")

        user = UsuarioModel.autenticar(identificador, senha)
        if user:
            session["user_id"] = user["id"]
            session["user_nome"] = user["nome"]
            session["user_tipo"] = user["tipo"]
            session["user_email"] = user["email"]
            session["aluno_id"] = user.get("aluno_id")
            flash(f"Bem-vindo(a) ao UniBook, {user['nome']}! (Perfil: {user['tipo'].upper()})", "sucesso")
            return redirect(url_for("books.listar_livros"))
        else:
            flash("Credenciais inválidas. Tente novamente ou use o Login Rápido.", "erro")

    return render_template("login.html")

@auth_bp.route("/login-rapido/<perfil>", methods=["POST", "GET"])
def login_rapido(perfil):
    """
    Login Rápido em 1 clique para os 3 perfis:
    - 'admin': Administrador (acesso irrestrito)
    - 'bibliotecario': Bibliotecário (acervo, renovações, multas)
    - 'aluno': Aluno (empréstimos próprios, avaliações, consulta)
    """
    perfis_validos = ["admin", "bibliotecario", "aluno"]
    tipo = perfil if perfil in perfis_validos else "aluno"
    user = UsuarioModel.obter_perfil_rapido(tipo=tipo)

    if user:
        session["user_id"] = user["id"]
        session["user_nome"] = user["nome"]
        session["user_tipo"] = user["tipo"]
        session["user_email"] = user["email"]
        session["aluno_id"] = user.get("aluno_id")
        flash(f"Conectado como {user['nome']} ({user['tipo'].upper()})!", "sucesso")
        return redirect(url_for("books.listar_livros"))
    else:
        flash("Perfil rápido não encontrado. Inicialize o banco de dados.", "erro")
        return redirect(url_for("auth.login_view"))

@auth_bp.route("/logout")
def logout_view():
    """Encerra a sessão do usuário."""
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("auth.login_view"))
