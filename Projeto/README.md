# 📚 UniBook - Portal de Consulta ao Acervo (UniEnsino)

Sistema web em **Python (Flask)** para organização, acervo e gestão da biblioteca da **Faculdade UniEnsino**.

---

## 🎨 Identidade Visual
- **Fundo Branco Limpo** em todo o site.
- **Paleta Oficial baseada na Logo**:
  - **Azul Marinho**: `#0a3871`
  - **Vermelho Carmim**: `#d32f2f`
- Imagem da logo oficial `UniBook` inserida com destaque na tela inicial, no cabeçalho e no formulário de login.

---

## 👥 Matriz de Perfis e Permissões (Roles)

O sistema possui 3 perfis distintos para navegação e testes rápidos:

### 1. 🎓 Aluno UniEnsino
- **Acesso focado e seguro**:
  - Consultar o acervo com filtros dinâmicos de temas (**Comédia, Romance, Ficção Científica**, etc.).
  - **Pegar livros emprestados** para si mesmo.
  - Acessar a tela **"Meus Empréstimos"** com controle de prazos de entrega.
  - **Avaliar livros** com nota de 1 a 5 estrelas e comentários/resenhas.
  - **BLOQUEADO**: Não pode excluir livros, não pode excluir alunos, não pode cadastrar livros/alunos, não pode renovar por conta própria e não pode aplicar multas.

### 2. 📚 Bibliotecário
- **Gestão diária da biblioteca**:
  - Cadastrar novos livros no acervo.
  - Excluir livros desatualizados/danificados.
  - Registrar empréstimos para qualquer estudante.
  - **Renovar prazos de livros (+7 dias)**.
  - **Aplicar multas** por atraso ou danos com valor em R$ e motivo.
  - Dar baixa/quitar multas.
  - Visualizar listagem de alunos.
  - **REGRA RESTRITIVA**: **Não pode alterar o e-mail institucional dos alunos** sem a devida autorização do titular (campo protegido como somente leitura e validado no backend).

### 3. 🛡️ Administrador
- **Acesso total e irrestrito**:
  - Todas as funções do acervo e empréstimos.
  - Gerenciamento completo de alunos (incluindo alteração de e-mails cadastrais e exclusão definitiva).

---

## ⚡ Como Rodar o UniBook

### 1. Ativar o Ambiente Virtual
No terminal PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

### 2. Iniciar o Servidor
```powershell
.venv\Scripts\python src/main.py
```
Acesse no navegador: 👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🚀 Login Rápido em 1 Clique (Demonstração)
Na tela de login, clique em qualquer um dos 3 botões dedicados:
- **[🛡️ Administrador]** -> Conecta como Administrador
- **[📚 Bibliotecário]** -> Conecta como Bibliotecário
- **[🎓 Aluno UniEnsino]** -> Conecta como Lucas Silva (Aluno)

---

## 🧪 Testes Automatizados em Python

Execute a suíte de testes com 19 testes automatizados:
```powershell
.venv\Scripts\python -m unittest discover -s src/tests
```
Cobre autenticação, restrições de permissões do aluno e do bibliotecário, empréstimos, renovações, multas e avaliações.
