from src.database import get_db_connection

class AvaliacaoModel:
    @staticmethod
    def adicionar(livro_id, aluno_id, aluno_nome, nota, comentario="", db_path=None):
        """Registra uma avaliação do livro feita por um aluno (nota 1 a 5 estrelas)."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO avaliacoes (livro_id, aluno_id, aluno_nome, nota, comentario)
                VALUES (?, ?, ?, ?, ?)
            """, (livro_id, aluno_id, aluno_nome.strip(), int(nota), comentario.strip()))
            conn.commit()
            return {"sucesso": True, "id": cursor.lastrowid}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def listar_por_livro(livro_id, db_path=None):
        """Retorna todas as avaliações de um livro em ordem decrescente."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM avaliacoes 
            WHERE livro_id = ? 
            ORDER BY criado_em DESC
        """, (livro_id,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def calcular_estatisticas_livro(livro_id, db_path=None):
        """Calcula a nota média e quantidade de avaliações do livro."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as total, AVG(nota) as media 
            FROM avaliacoes 
            WHERE livro_id = ?
        """, (livro_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row["total"] > 0:
            return {
                "total": row["total"],
                "media": round(row["media"], 1)
            }
        return {"total": 0, "media": 0.0}
