from src.database import get_db_connection

class AlunoModel:
    @staticmethod
    def cadastrar(nome, matricula, curso, email, db_path=None):
        """Cadastra um novo aluno da UniEnsino."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO alunos (nome, matricula, curso, email)
                VALUES (?, ?, ?, ?)
            """, (nome.strip(), matricula.strip(), curso.strip(), email.strip()))
            conn.commit()
            aluno_id = cursor.lastrowid
            return {"sucesso": True, "id": aluno_id}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def atualizar(aluno_id, nome, matricula, curso, email, usuario_tipo="admin", db_path=None):
        """
        Atualiza os dados de um aluno.
        REGRA DO TRABALHO: O Bibliotecário NÃO pode alterar o e-mail do aluno sem autorização!
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
            aluno_atual = cursor.fetchone()
            if not aluno_atual:
                return {"sucesso": False, "erro": "Aluno não encontrado."}

            # Verificação de segurança de permissão de e-mail para o Bibliotecário
            if usuario_tipo == "bibliotecario" and email.strip().lower() != aluno_atual["email"].strip().lower():
                return {
                    "sucesso": False,
                    "erro": "O Bibliotecário não tem permissão para alterar o e-mail institucional do aluno sem autorização prévia."
                }

            cursor.execute("""
                UPDATE alunos 
                SET nome = ?, matricula = ?, curso = ?, email = ?
                WHERE id = ?
            """, (nome.strip(), matricula.strip(), curso.strip(), email.strip(), aluno_id))
            conn.commit()
            return {"sucesso": True}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    @staticmethod
    def listar(busca=None, db_path=None):
        """Lista todos os alunos com opção de busca por nome ou matrícula."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        if busca:
            termo = f"%{busca.strip()}%"
            cursor.execute("""
                SELECT * FROM alunos 
                WHERE nome LIKE ? OR matricula LIKE ? OR curso LIKE ?
                ORDER BY nome ASC
            """, (termo, termo, termo))
        else:
            cursor.execute("SELECT * FROM alunos ORDER BY nome ASC")
        alunos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return alunos

    @staticmethod
    def buscar_por_id(aluno_id, db_path=None):
        """Busca um aluno específico pelo ID."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def buscar_por_matricula(matricula, db_path=None):
        """Busca aluno pela matrícula/RA."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE matricula = ?", (matricula.strip(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def excluir(aluno_id, db_path=None):
        """Exclui um aluno do sistema."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        linhas_afetadas = cursor.rowcount
        conn.commit()
        conn.close()
        return linhas_afetadas > 0
