import unittest
import os
import tempfile
from src.main import create_app
from src.seed import seed_database
from src.models.aluno import AlunoModel

class TestAlunos(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        seed_database(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()
        # Autentica como admin para operações de alunos
        self.client.get("/login-rapido/admin")

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_cadastrar_e_excluir_aluno(self):
        """Valida o cadastro de um aluno da UniEnsino e sua posterior exclusão."""
        res = AlunoModel.cadastrar(
            nome="Carlos Eduardo de Oliveira",
            matricula="20269999",
            curso="Ciência da Computação",
            email="carlos.oliveira@uniensino.edu.br",
            db_path=self.db_path
        )
        self.assertTrue(res.get("sucesso"))
        aluno_id = res["id"]

        # Busca por ID
        aluno = AlunoModel.buscar_por_id(aluno_id, db_path=self.db_path)
        self.assertIsNotNone(aluno)
        self.assertEqual(aluno["matricula"], "20269999")

        # Excluir aluno
        excluido = AlunoModel.excluir(aluno_id, db_path=self.db_path)
        self.assertTrue(excluido)

        # Confirmar remoção
        aluno_removido = AlunoModel.buscar_por_id(aluno_id, db_path=self.db_path)
        self.assertIsNone(aluno_removido)

    def test_evitar_matricula_duplicada(self):
        """Valida que o sistema não permite cadastrar dois alunos com a mesma matrícula."""
        res1 = AlunoModel.cadastrar(
            nome="Aluno 1",
            matricula="20268888",
            curso="Direito",
            email="aluno1@uniensino.edu.br",
            db_path=self.db_path
        )
        self.assertTrue(res1.get("sucesso"))

        res2 = AlunoModel.cadastrar(
            nome="Aluno 2",
            matricula="20268888",
            curso="Administração",
            email="aluno2@uniensino.edu.br",
            db_path=self.db_path
        )
        self.assertFalse(res2.get("sucesso"))
        self.assertIn("UNIQUE", res2.get("erro", ""))

if __name__ == "__main__":
    unittest.main()
