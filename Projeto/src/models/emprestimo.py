from datetime import date, timedelta
from src.database import get_db_connection

class EmprestimoModel:
    @staticmethod
    def emprestar(livro_id, aluno_id, dias=14, db_path=None):
        """
        Realiza o empréstimo de um livro para o aluno.
        Decrementa a quantidade disponível e define o prazo de devolução.
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            # 1. Verifica se há exemplar disponível
            cursor.execute("SELECT quantidade, titulo FROM livros WHERE id = ?", (livro_id,))
            livro = cursor.fetchone()
            if not livro:
                return {"sucesso": False, "erro": "Livro não encontrado."}
            if livro["quantidade"] <= 0:
                return {"sucesso": False, "erro": f"Não há exemplares disponíveis de '{livro['titulo']}' no momento."}

            # 2. Registra o empréstimo
            hoje = date.today()
            data_prevista = hoje + timedelta(days=dias)

            cursor.execute("""
                INSERT INTO emprestimos (livro_id, aluno_id, data_emprestimo, data_devolucao_prevista, status)
                VALUES (?, ?, ?, ?, 'ativo')
            """, (livro_id, aluno_id, hoje.isoformat(), data_prevista.isoformat()))
            emprestimo_id = cursor.lastrowid

            # 3. Decrementa o exemplar do acervo
            cursor.execute("""
                UPDATE livros SET quantidade = quantidade - 1 WHERE id = ?
            """, (livro_id,))

            conn.commit()
            return {"sucesso": True, "id": emprestimo_id, "data_prevista": data_prevista.strftime("%d/%m/%Y")}
        except Exception as e:
            conn.rollback()
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def devolver(emprestimo_id, db_path=None):
        """Marca o empréstimo como devolvido e devolve o exemplar ao estoque do acervo."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT livro_id, status FROM emprestimos WHERE id = ?", (emprestimo_id,))
            emp = cursor.fetchone()
            if not emp:
                return {"sucesso": False, "erro": "Empréstimo não encontrado."}
            if emp["status"] == "devolvido":
                return {"sucesso": False, "erro": "Este empréstimo já foi finalizado."}

            hoje = date.today().isoformat()
            cursor.execute("""
                UPDATE emprestimos 
                SET status = 'devolvido', data_devolucao_real = ? 
                WHERE id = ?
            """, (hoje, emprestimo_id))

            # Devolve 1 exemplar ao livro
            cursor.execute("""
                UPDATE livros SET quantidade = quantidade + 1 WHERE id = ?
            """, (emp["livro_id"],))

            conn.commit()
            return {"sucesso": True}
        except Exception as e:
            conn.rollback()
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def renovar(emprestimo_id, dias_adicionais=7, db_path=None):
        """
        Renova o empréstimo estendendo o prazo de devolução.
        Função exclusiva para Bibliotecário e Administrador.
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM emprestimos WHERE id = ?", (emprestimo_id,))
            emp = cursor.fetchone()
            if not emp:
                return {"sucesso": False, "erro": "Empréstimo não encontrado."}
            if emp["status"] == "devolvido":
                return {"sucesso": False, "erro": "Não é possível renovar um livro já devolvido."}

            # Calcula nova data prevista a partir da data atual prevista ou de hoje
            data_atual = date.fromisoformat(emp["data_devolucao_prevista"])
            nova_data = max(data_atual, date.today()) + timedelta(days=dias_adicionais)

            cursor.execute("""
                UPDATE emprestimos 
                SET data_devolucao_prevista = ?, 
                    renovacoes = renovacoes + 1,
                    status = 'renovado'
                WHERE id = ?
            """, (nova_data.isoformat(), emprestimo_id))

            conn.commit()
            return {"sucesso": True, "nova_data": nova_data.strftime("%d/%m/%Y")}
        except Exception as e:
            conn.rollback()
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def aplicar_multa(emprestimo_id, valor, motivo, db_path=None):
        """
        Aplica multa a um empréstimo por atraso ou danos.
        Função do Bibliotecário e Administrador.
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE emprestimos 
                SET multa_valor = ?, multa_motivo = ?, multa_paga = 0
                WHERE id = ?
            """, (float(valor), motivo.strip(), emprestimo_id))
            conn.commit()
            return {"sucesso": True}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def quitar_multa(emprestimo_id, db_path=None):
        """Dá baixa em uma multa aplicada."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE emprestimos SET multa_paga = 1 WHERE id = ?", (emprestimo_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def listar_todos(status_filtro=None, db_path=None):
        """Lista empréstimos com dados do livro e do aluno."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        query = """
            SELECT e.*, 
                   l.titulo AS livro_titulo, l.autor AS livro_autor, l.tema AS livro_tema, l.capa_url AS livro_capa_url,
                   a.nome AS aluno_nome, a.matricula AS aluno_matricula, a.curso AS aluno_curso, a.email AS aluno_email
            FROM emprestimos e
            JOIN livros l ON e.livro_id = l.id
            JOIN alunos a ON e.aluno_id = a.id
        """
        params = []
        if status_filtro and status_filtro != "todos":
            query += " WHERE e.status = ?"
            params.append(status_filtro)

        query += " ORDER BY e.id DESC"
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def listar_por_aluno(aluno_id, db_path=None):
        """Lista os empréstimos específicos de um aluno."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, 
                   l.titulo AS livro_titulo, l.autor AS livro_autor, l.tema AS livro_tema, l.capa_url AS livro_capa_url,
                   a.nome AS aluno_nome, a.matricula AS aluno_matricula
            FROM emprestimos e
            JOIN livros l ON e.livro_id = l.id
            JOIN alunos a ON e.aluno_id = a.id
            WHERE e.aluno_id = ?
            ORDER BY e.id DESC
        """, (aluno_id,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
