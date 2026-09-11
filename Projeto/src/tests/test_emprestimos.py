import unittest
import os
import tempfile
from src.main import create_app
from src.seed import seed_database
from src.models.emprestimo import EmprestimoModel
from src.models.livro import LivroModel

class TestEmprestimos(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        seed_database(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_aluno_pega_livro_emprestado(self):
        """Valida que o aluno consegue emprestar livro para si e decrementa o estoque."""
        self.client.get("/login-rapido/aluno")
        livro = LivroModel.buscar_por_id(1, db_path=self.db_path)
        qtd_inicial = livro["quantidade"]

        res = self.client.post("/emprestimos/solicitar/1", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Empréstimo registrado com sucesso".encode("utf-8"), res.data)

        livro_pos = LivroModel.buscar_por_id(1, db_path=self.db_path)
        self.assertEqual(livro_pos["quantidade"], qtd_inicial - 1)

    def test_bibliotecario_renova_emprestimo(self):
        """Valida que o bibliotecário consegue renovar o prazo do livro."""
        self.client.get("/login-rapido/bibliotecario")
        emp = EmprestimoModel.listar_todos(db_path=self.db_path)[0]

        res = self.client.post(f"/emprestimos/{emp['id']}/renovar", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Empréstimo renovado com sucesso".encode("utf-8"), res.data)

    def test_bibliotecario_aplica_multa(self):
        """Valida que o bibliotecário pode aplicar multa a um empréstimo."""
        self.client.get("/login-rapido/bibliotecario")
        emp = EmprestimoModel.listar_todos(db_path=self.db_path)[0]

        res = self.client.post(f"/emprestimos/{emp['id']}/multa", data={
            "valor": "12.50",
            "motivo": "Atraso na entrega"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Multa de R$ 12.50 aplicada".encode("utf-8"), res.data)

    def test_devolucao_restaura_estoque(self):
        """Valida que a devolução de um livro restaura a quantidade de exemplares."""
        self.client.get("/login-rapido/bibliotecario")
        emp = EmprestimoModel.listar_todos(db_path=self.db_path)[0]
        livro_antes = LivroModel.buscar_por_id(emp["livro_id"], db_path=self.db_path)

        res = self.client.post(f"/emprestimos/{emp['id']}/devolver", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Livro devolvido com sucesso".encode("utf-8"), res.data)

        livro_depois = LivroModel.buscar_por_id(emp["livro_id"], db_path=self.db_path)
        self.assertEqual(livro_depois["quantidade"], livro_antes["quantidade"] + 1)

if __name__ == "__main__":
    unittest.main()
