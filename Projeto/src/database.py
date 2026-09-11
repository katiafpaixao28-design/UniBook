import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import sqlite3
from src.config import DATABASE_PATH

def get_db_connection(db_path=None):
    """Retorna uma conexão ativa com o banco SQLite."""
    if db_path is None:
        try:
            from flask import current_app
            if current_app:
                db_path = current_app.config.get("DATABASE", DATABASE_PATH)
        except Exception:
            pass

    path = db_path or DATABASE_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=None):
    """Inicializa as tabelas do banco de dados e executa migrações automáticas."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Tabela de Usuários (com os 3 perfis: admin, bibliotecario, aluno)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'aluno', -- 'admin', 'bibliotecario', 'aluno'
        matricula TEXT UNIQUE,
        aluno_id INTEGER,
        FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE SET NULL
    );
    """)

    # Migração para aluno_id
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas_usuario = [row["name"] for row in cursor.fetchall()]
    if "aluno_id" not in colunas_usuario:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN aluno_id INTEGER")

    # 2. Tabela de Alunos da Faculdade UniEnsino
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        matricula TEXT UNIQUE NOT NULL,
        curso TEXT NOT NULL,
        email TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Tabela de Livros do Acervo (com capa_url)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        tema TEXT NOT NULL,
        ano INTEGER,
        quantidade INTEGER DEFAULT 1,
        sinopse TEXT,
        capa_url TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migração para capa_url em bancos já existentes
    cursor.execute("PRAGMA table_info(livros)")
    colunas_livros = [row["name"] for row in cursor.fetchall()]
    if "capa_url" not in colunas_livros:
        cursor.execute("ALTER TABLE livros ADD COLUMN capa_url TEXT")

    # 4. Tabela de Empréstimos (com renovações e multas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emprestimos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livro_id INTEGER NOT NULL,
        aluno_id INTEGER NOT NULL,
        data_emprestimo DATE NOT NULL,
        data_devolucao_prevista DATE NOT NULL,
        data_devolucao_real DATE,
        renovacoes INTEGER DEFAULT 0,
        multa_valor REAL DEFAULT 0.0,
        multa_motivo TEXT,
        multa_paga INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'ativo', -- 'ativo', 'devolvido', 'renovado', 'atrasado'
        FOREIGN KEY (livro_id) REFERENCES livros (id) ON DELETE CASCADE,
        FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE CASCADE
    );
    """)

    # 5. Tabela de Avaliações de Livros (notas 1 a 5 estrelas e comentários)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livro_id INTEGER NOT NULL,
        aluno_id INTEGER,
        aluno_nome TEXT NOT NULL,
        nota INTEGER NOT NULL CHECK(nota >= 1 AND nota <= 5),
        comentario TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (livro_id) REFERENCES livros (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados do UniBook atualizado com suporte a capas de livros!")
