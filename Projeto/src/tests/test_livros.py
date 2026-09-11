import unittest
import os
import tempfile
from src.main import create_app
from src.seed import seed_database
from src.models.livro import LivroModel

class TestLivros(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        seed_database(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()
        # Autentica como admin para operações protegidas
        self.client.get("/login-rapido/admin")

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_filtrar_por_tema_comedia(self):
        """Valida que o filtro pelo tema Comédia retorna as obras corretas."""
        livros = LivroModel.listar(tema="Comédia", db_path=self.db_path)
        self.assertGreater(len(livros), 0)
        for livro in livros:
            self.assertEqual(livro["tema"], "Comédia")

    def test_filtrar_por_tema_romance(self):
        """Valida que o filtro pelo tema Romance retorna as obras corretas."""
        livros = LivroModel.listar(tema="Romance", db_path=self.db_path)
        self.assertGreater(len(livros), 0)
        for livro in livros:
            self.assertEqual(livro["tema"], "Romance")

    def test_adicionar_e_excluir_livro(self):
        """Valida a adição de um novo livro com capa e sua posterior exclusão."""
        # Adicionar
        res = LivroModel.adicionar(
            titulo="Livro de Teste de Humor",
            autor="Comediante Universitário",
            tema="Comédia",
            ano=2026,
            quantidade=2,
            sinopse="Uma obra divertida para testes unitários.",
            capa_url="https://covers.openlibrary.org/b/id/11153228-M.jpg",
            db_path=self.db_path
        )
        self.assertTrue(res.get("sucesso"))
        livro_id = res["id"]

        # Verificar se está na listagem com a capa
        livro = LivroModel.buscar_por_id(livro_id, db_path=self.db_path)
        self.assertIsNotNone(livro)
        self.assertEqual(livro["titulo"], "Livro de Teste de Humor")
        self.assertEqual(livro["capa_url"], "https://covers.openlibrary.org/b/id/11153228-M.jpg")

        # Excluir
        excluido = LivroModel.excluir(livro_id, db_path=self.db_path)
        self.assertTrue(excluido)

        # Confirmar que não existe mais
        livro_pos = LivroModel.buscar_por_id(livro_id, db_path=self.db_path)
        self.assertIsNone(livro_pos)

    def test_adicionar_livro_rapido_1_clique(self):
        """Valida o cadastro express em 1 clique via rota /livros/adicionar-rapido."""
        res = self.client.post("/livros/adicionar-rapido", data={
            "titulo": "Memórias Póstumas de Brás Cubas Express",
            "autor": "Machado de Assis",
            "tema": "Comédia",
            "ano": "1881",
            "quantidade": "4",
            "sinopse": "Edição express para alunos",
            "capa_url": "https://covers.openlibrary.org/b/id/10515152-M.jpg"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("adicionada ao acervo em 1 clique".encode("utf-8"), res.data)

        # Verifica presença no banco
        livros = LivroModel.listar(busca="Brás Cubas Express", db_path=self.db_path)
        self.assertEqual(len(livros), 1)
        self.assertIn("10515152", livros[0]["capa_url"])

if __name__ == "__main__":
    unittest.main()
