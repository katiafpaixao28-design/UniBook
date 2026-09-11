import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import sqlite3
from datetime import date, timedelta
from src.database import get_db_connection, init_db

def seed_database(db_path=None):
    """Popula o banco com dados iniciais completos, capas reais de livros e fluxos."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Alunos da Faculdade UniEnsino
    alunos = [
        ("Lucas Silva", "20261001", "Ciência da Computação", "lucas.silva@uniensino.edu.br"),
        ("Beatriz Souza", "20261002", "Engenharia de Software", "beatriz.souza@uniensino.edu.br"),
        ("Gabriel Ramos", "20261003", "Direito", "gabriel.ramos@uniensino.edu.br"),
        ("Camila Santos", "20261004", "Administração", "camila.santos@uniensino.edu.br"),
        ("Mariana Oliveira", "20261005", "Psicologia", "mariana.oliveira@uniensino.edu.br")
    ]
    for a in alunos:
        cursor.execute("""
            INSERT OR IGNORE INTO alunos (nome, matricula, curso, email)
            VALUES (?, ?, ?, ?)
        """, a)

    # 2. Usuários com os 3 Perfis Requisitados
    usuarios = [
        ("Administrador UniEnsino", "admin@uniensino.edu.br", "admin123", "admin", "ADM001", None),
        ("Bibliotecário UniEnsino", "bibliotecario@uniensino.edu.br", "biblio123", "bibliotecario", "BIB001", None),
        ("Lucas Silva (Aluno)", "aluno@uniensino.edu.br", "aluno123", "aluno", "20261001", 1)
    ]
    for u in usuarios:
        cursor.execute("""
            INSERT OR REPLACE INTO usuarios (nome, email, senha, tipo, matricula, aluno_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, u)

    # 3. Livros de Temas Variados com Capas em Alta Resolução
    livros = [
        (
            "O Auto da Compadecida", 
            "Ariano Suassuna", 
            "Comédia", 
            1955, 
            3, 
            "Clássico da literatura brasileira repleto de humor, esperteza e regionalismo nordestino.",
            "https://covers.openlibrary.org/b/id/11153228-M.jpg"
        ),
        (
            "O Guia do Mochileiro das Galáxias", 
            "Douglas Adams", 
            "Comédia", 
            1979, 
            4, 
            "A hilária saga intergaláctica com toalhas, computadores pensantes e a resposta fundamental sobre a vida.",
            "https://covers.openlibrary.org/b/id/8231990-M.jpg"
        ),
        (
            "Orgulho e Preconceito", 
            "Jane Austen", 
            "Romance", 
            1813, 
            5, 
            "Uma das histórias de amor mais influentes da literatura mundial sobre Elizabeth Bennet e o Sr. Darcy.",
            "https://covers.openlibrary.org/b/id/8114429-M.jpg"
        ),
        (
            "Dom Casmurro", 
            "Machado de Assis", 
            "Romance", 
            1899, 
            4, 
            "A inesquecível narrativa de Bento Santiago e Capitu nos dilemas do amor e da dúvida.",
            "https://covers.openlibrary.org/b/id/647501-M.jpg"
        ),
        (
            "A Culpa é das Estrelas", 
            "John Green", 
            "Romance", 
            2012, 
            3, 
            "Um romance jovem emocionante e comovente sobre Hazel Grace e Augustus Waters.",
            "https://covers.openlibrary.org/b/id/7287998-M.jpg"
        ),
        (
            "Duna", 
            "Frank Herbert", 
            "Ficção Científica", 
            1965, 
            3, 
            "Épico de ficção científica no planeta desértico Arrakis envolvendo intrigas políticas e misticismo.",
            "https://covers.openlibrary.org/b/id/10398657-M.jpg"
        ),
        (
            "Fundação", 
            "Isaac Asimov", 
            "Ficção Científica", 
            1951, 
            4, 
            "A obra-prima sobre a psicohistória e a preservação do conhecimento galáctico.",
            "https://covers.openlibrary.org/b/id/8328173-M.jpg"
        ),
        (
            "O Iluminado", 
            "Stephen King", 
            "Suspense/Terror", 
            1977, 2, 
            "Obra magistral do terror psicológico no isolado hotel Overlook durante o rigoroso inverno.",
            "https://covers.openlibrary.org/b/id/10521270-M.jpg"
        ),
        (
            "Código Limpo (Clean Code)", 
            "Robert C. Martin", 
            "Acadêmico/Técnico", 
            2008, 
            6, 
            "Guia essencial sobre boas práticas, clareza e refatoração de código no desenvolvimento de software.",
            "https://covers.openlibrary.org/b/id/8447833-M.jpg"
        ),
        (
            "O Senhor dos Anéis: A Sociedade do Anel", 
            "J.R.R. Tolkien", 
            "Fantasia", 
            1954, 
            5, 
            "A grande jornada para salvar a Terra-média destruindo o Um Anel nas chamas de Mordor.",
            "https://covers.openlibrary.org/b/id/8234382-M.jpg"
        )
    ]
    for l in livros:
        cursor.execute("SELECT id FROM livros WHERE titulo = ? AND autor = ?", (l[0], l[1]))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                INSERT INTO livros (titulo, autor, tema, ano, quantidade, sinopse, capa_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, l)
        else:
            # Atualiza capa caso já exista
            cursor.execute("UPDATE livros SET capa_url = ? WHERE id = ?", (l[6], row["id"]))

    # 4. Avaliações de Exemplo pelos Alunos
    cursor.execute("SELECT id FROM livros WHERE titulo = 'O Auto da Compadecida'")
    auto = cursor.fetchone()
    if auto:
        cursor.execute("SELECT id FROM avaliacoes WHERE livro_id = ?", (auto["id"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO avaliacoes (livro_id, aluno_id, aluno_nome, nota, comentario)
                VALUES (?, 1, 'Lucas Silva', 5, 'Obra espetacular e muito engraçada! O Chicó e o João Grilo são impagáveis.')
            """, (auto["id"],))

    cursor.execute("SELECT id FROM livros WHERE titulo = 'Orgulho e Preconceito'")
    orgulho = cursor.fetchone()
    if orgulho:
        cursor.execute("SELECT id FROM avaliacoes WHERE livro_id = ?", (orgulho["id"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO avaliacoes (livro_id, aluno_id, aluno_nome, nota, comentario)
                VALUES (?, 1, 'Lucas Silva', 5, 'Excelente romance de época, diálogos fantásticos e leitura muito agradável.')
            """, (orgulho["id"],))

    # 5. Empréstimo Inicial de Demonstração
    cursor.execute("SELECT id FROM emprestimos LIMIT 1")
    if not cursor.fetchone() and auto:
        hoje = date.today()
        prev = hoje + timedelta(days=14)
        cursor.execute("""
            INSERT INTO emprestimos (livro_id, aluno_id, data_emprestimo, data_devolucao_prevista, status)
            VALUES (?, 1, ?, ?, 'ativo')
        """, (auto["id"], hoje.isoformat(), prev.isoformat()))
        cursor.execute("UPDATE livros SET quantidade = quantidade - 1 WHERE id = ?", (auto["id"],))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()
    print("Dados populados com sucesso com capas reais e 3 perfis!")
