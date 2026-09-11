import unittest
import os
import tempfile
from src.main import create_app
from src.seed import seed_database
from src.models.avaliacao import AvaliacaoModel
from src.models.livro import LivroModel

class TestAvaliacoes(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        seed_database(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_aluno_avalia_livro(self):
        """Valida que o aluno consegue avaliar um livro com nota de 1 a 5 estrelas."""
        self.client.get("/login-rapido/aluno")

        res = self.client.post("/livros/1/avaliar", data={
            "nota": "5",
            "comentario": "Excelente história, ri muito com os personagens!"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Sua avaliação foi registrada com sucesso".encode("utf-8"), res.data)

        # Verifica persistência no modelo
        avaliacoes = AvaliacaoModel.listar_por_livro(1, db_path=self.db_path)
        self.assertGreater(len(avaliacoes), 0)
        stats = AvaliacaoModel.calcular_estatisticas_livro(1, db_path=self.db_path)
        self.assertGreater(stats["media"], 0)

if __name__ == "__main__":
    unittest.main()
