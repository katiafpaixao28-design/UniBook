from src.database import get_db_connection

class LivroModel:
    @staticmethod
    def adicionar(titulo, autor, tema, ano=None, quantidade=1, sinopse="", capa_url=None, db_path=None):
        """Adiciona um novo livro ao acervo do UniBook, incluindo URL da capa."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO livros (titulo, autor, tema, ano, quantidade, sinopse, capa_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                titulo.strip(), 
                autor.strip(), 
                tema.strip(), 
                ano, 
                quantidade, 
                sinopse.strip() if sinopse else "", 
                capa_url.strip() if capa_url else None
            ))
            conn.commit()
            livro_id = cursor.lastrowid
            return {"sucesso": True, "id": livro_id}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def listar(tema=None, busca=None, db_path=None):
        """
        Lista livros com dados agregados de avaliações (média e total de notas)
        e imagem de capa para renderização ao lado do título.
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT l.*, 
                   COUNT(a.id) AS total_avaliacoes,
                   COALESCE(AVG(a.nota), 0.0) AS media_avaliacoes
            FROM livros l
            LEFT JOIN avaliacoes a ON l.id = a.livro_id
            WHERE 1=1
        """
        params = []

        if tema and tema != "Todos":
            query += " AND l.tema = ?"
            params.append(tema)

        if busca:
            query += " AND (l.titulo LIKE ? OR l.autor LIKE ?)"
            termo = f"%{busca.strip()}%"
            params.extend([termo, termo])

        query += " GROUP BY l.id ORDER BY l.titulo ASC"
        cursor.execute(query, params)
        livros = []
        for row in cursor.fetchall():
            d = dict(row)
            d["media_avaliacoes"] = round(d["media_avaliacoes"], 1)
            livros.append(d)
        conn.close()
        return livros

    @staticmethod
    def buscar_por_id(livro_id, db_path=None):
        """Busca um livro específico pelo ID com suas avaliações e capa."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, 
                   COUNT(a.id) AS total_avaliacoes,
                   COALESCE(AVG(a.nota), 0.0) AS media_avaliacoes
            FROM livros l
            LEFT JOIN avaliacoes a ON l.id = a.livro_id
            WHERE l.id = ?
            GROUP BY l.id
        """, (livro_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            d["media_avaliacoes"] = round(d["media_avaliacoes"], 1)
            return d
        return None

    @staticmethod
    def excluir(livro_id, db_path=None):
        """Exclui um livro do acervo."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        afetados = cursor.rowcount
        conn.commit()
        conn.close()
        return afetados > 0

    @staticmethod
    def estatisticas(db_path=None):
        """Retorna contadores de livros e exemplares por tema."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_titulos, COALESCE(SUM(quantidade), 0) AS total_exemplares FROM livros")
        geral = dict(cursor.fetchone())

        cursor.execute("""
            SELECT tema, COUNT(*) AS total 
            FROM livros 
            GROUP BY tema 
            ORDER BY total DESC
        """)
        por_tema = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"geral": geral, "por_tema": por_tema}
