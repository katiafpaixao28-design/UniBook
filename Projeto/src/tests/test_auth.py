import unittest
import os
import tempfile
from src.main import create_app
from src.seed import seed_database

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        seed_database(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_login_rapido_admin(self):
        """Valida que o login rápido de Administrador conecta com perfil total."""
        response = self.client.get("/login-rapido/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Administrador UniEnsino".encode("utf-8"), response.data)

    def test_login_rapido_bibliotecario(self):
        """Valida que o login rápido de Bibliotecário conecta com perfil intermediário."""
        response = self.client.get("/login-rapido/bibliotecario", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bibliotecário UniEnsino".encode("utf-8"), response.data)

    def test_login_rapido_aluno(self):
        """Valida que o login rápido de Aluno conecta com perfil restrito."""
        response = self.client.get("/login-rapido/aluno", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Lucas Silva".encode("utf-8"), response.data)

    def test_logout(self):
        """Valida o logout seguro da sessão."""
        self.client.get("/login-rapido/aluno")
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sessão encerrada".encode("utf-8"), response.data)

if __name__ == "__main__":
    unittest.main()
