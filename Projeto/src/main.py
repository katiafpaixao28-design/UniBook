import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, session
from src.config import SECRET_KEY, DATABASE_PATH, TEMAS_LIVROS
from src.database import init_db
from src.seed import seed_database
from src.routes.auth_routes import auth_bp
from src.routes.book_routes import book_bp
from src.routes.student_routes import student_bp
from src.routes.loan_routes import loan_bp

def create_app(test_config=None):
    """Cria e configura a aplicação web UniBook em padrão Pythonic."""
    app = Flask(__name__, 
                template_folder="templates", 
                static_folder="static")

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DATABASE"] = DATABASE_PATH

    if test_config:
        app.config.update(test_config)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(loan_bp)

    # Context Processor para variáveis globais nos templates
    @app.context_processor
    def inject_global_vars():
        return {
            "instituicao": "Faculdade UniEnsino",
            "sistema_nome": "UniBook",
            "usuario_logado": session.get("user_nome"),
            "usuario_tipo": session.get("user_tipo"),
            "aluno_id": session.get("aluno_id"),
            "todos_temas": TEMAS_LIVROS
        }

    return app

app = create_app()

if __name__ == "__main__":
    if not os.path.exists(DATABASE_PATH):
        print("Criando banco e populando dados de demonstração da UniEnsino...")
        seed_database()
    else:
        init_db()

    print("=" * 60)
    print("UniBook - Portal de Consulta ao Acervo - Faculdade UniEnsino")
    print("Servidor iniciado em: http://127.0.0.1:5000")
    print("3 Perfis de Login Rápido disponíveis (Admin, Bibliotecário, Aluno)")
    print("=" * 60)
    app.run(debug=True, port=5000)
