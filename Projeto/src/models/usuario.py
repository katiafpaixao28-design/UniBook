from src.database import get_db_connection

class UsuarioModel:
    @staticmethod
    def autenticar(identificador, senha, db_path=None):
        """Autentica usuário por e-mail ou matrícula/RA."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        termo = identificador.strip()
        cursor.execute("""
            SELECT * FROM usuarios 
            WHERE (email = ? OR matricula = ?) AND senha = ?
        """, (termo, termo, senha.strip()))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def buscar_por_id(user_id, db_path=None):
        """Busca usuário pelo ID."""
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def obter_perfil_rapido(tipo="admin", db_path=None):
        """
        Retorna um usuário de perfil rápido pré-configurado:
        - 'admin': Administrador com acesso total
        - 'bibliotecario': Bibliotecário com acervo, renovações e multas
        - 'aluno': Aluno com consulta, empréstimos próprios e avaliações
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE tipo = ? LIMIT 1", (tipo,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
