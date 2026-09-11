import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "unibook.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "unibook-uniensino-chave-secreta-2026")

# Temas/Gêneros padrão do acervo
TEMAS_LIVROS = [
    "Comédia",
    "Romance",
    "Ficção Científica",
    "Suspense/Terror",
    "Acadêmico/Técnico",
    "Fantasia",
    "Aventura",
    "Drama"
]

# Cursos padrão da UniEnsino
CURSOS_UNIENSINO = [
    "Ciência da Computação",
    "Sistemas de Informação",
    "Engenharia de Software",
    "Administração",
    "Direito",
    "Pedagogia",
    "Psicologia",
    "Enfermagem"
]
