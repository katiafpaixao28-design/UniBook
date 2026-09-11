import unittest
import os
import tempfile
from src.main import create_app
from src.seed import seed_database
from src.models.aluno import AlunoModel
from src.models.livro import LivroModel

class TestPermissoes(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        seed_database(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_aluno_bloqueado_de_excluir_livro(self):
        """Valida que o Aluno NÃO tem permissão para excluir livros do acervo."""
        # 1. Conecta como Aluno
        self.client.get("/login-rapido/aluno")
        livros = LivroModel.listar(db_path=self.db_path)
        livro_id = livros[0]["id"]

        # 2. Tenta excluir livro
        res = self.client.post(f"/livros/{livro_id}/excluir", follow_redirects=True)
        self.assertIn("Acesso não permitido".encode("utf-8"), res.data)

        # 3. Garante que o livro NÃO foi excluído
        livro = LivroModel.buscar_por_id(livro_id, db_path=self.db_path)
        self.assertIsNotNone(livro)

    def test_aluno_bloqueado_de_excluir_aluno(self):
        """Valida que o Aluno NÃO tem permissão para excluir alunos."""
        self.client.get("/login-rapido/aluno")
        res = self.client.post("/alunos/1/excluir", follow_redirects=True)
        self.assertIn("Acesso não permitido".encode("utf-8"), res.data)

    def test_aluno_bloqueado_de_adicionar_livro(self):
        """Valida que o Aluno NÃO tem permissão para cadastrar livros."""
        self.client.get("/login-rapido/aluno")
        res = self.client.post("/livros/novo", data={
            "titulo": "Tentativa Aluno",
            "autor": "Aluno",
            "tema": "Comédia"
        }, follow_redirects=True)
        self.assertIn("Acesso não permitido".encode("utf-8"), res.data)

    def test_bibliotecario_bloqueado_de_alterar_email_aluno(self):
        """
        REGRA DO TRABALHO:
        O Bibliotecário pode tudo no acervo/empréstimos, mas NÃO pode alterar o e-mail do aluno sem autorização!
        """
        self.client.get("/login-rapido/bibliotecario")
        aluno = AlunoModel.buscar_por_id(1, db_path=self.db_path)
        email_original = aluno["email"]

        # Bibliotecário tenta alterar o e-mail do aluno
        res = self.client.post("/alunos/1/editar", data={
            "nome": aluno["nome"],
            "matricula": aluno["matricula"],
            "curso": aluno["curso"],
            "email": "email_alterado_sem_autorizacao@uniensino.edu.br"
        }, follow_redirects=True)

        self.assertIn("não tem permissão para alterar o e-mail".encode("utf-8"), res.data)

        # Garante que o e-mail permaneceu o original no banco
        aluno_pos = AlunoModel.buscar_por_id(1, db_path=self.db_path)
        self.assertEqual(aluno_pos["email"], email_original)

    def test_admin_pode_alterar_email_aluno(self):
        """Valida que o Administrador possui permissão para atualizar o e-mail institucional."""
        self.client.get("/login-rapido/admin")
        aluno = AlunoModel.buscar_por_id(1, db_path=self.db_path)

        res = self.client.post("/alunos/1/editar", data={
            "nome": aluno["nome"],
            "matricula": aluno["matricula"],
            "curso": aluno["curso"],
            "email": "lucas.oficial@uniensino.edu.br"
        }, follow_redirects=True)

        self.assertIn("atualizados com sucesso".encode("utf-8"), res.data)
        aluno_pos = AlunoModel.buscar_por_id(1, db_path=self.db_path)
        self.assertEqual(aluno_pos["email"], "lucas.oficial@uniensino.edu.br")

if __name__ == "__main__":
    unittest.main()
