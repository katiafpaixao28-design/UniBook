# SPRINT 1: FUNDAÇÃO DA API E SUÍTE DE TESTE DA LIVRARIA
## Objetivo: Inicializar o ambiente virtual em Python e garantir que um endpoint de saúde responda com testes ativos.
### Requisitos Técnicos:
1. Usar o gerenciador de pacotes `uv` para inicializar o ambiente virtual e gerenciar dependências.
2. Adicionar as dependências: `fastapi`, `uvicorn`, `pydantic>=2.0`, `sqlalchemy>=2.0`, `pytest`.
3. Adicionar as ferramentas de análise estática e formatação: `ruff` e `mypy`.
4. Criar o arquivo `src/main.py` com uma aplicação FastAPI simples que contenha a rota:
- GET `/health` -> Deve retornar o JSON: {"status": "ok", "service": "livraria-api"}
5. Criar o teste em `tests/test_main.py` para verificar se a chamada ao endpoint `/health` retorna status code 200.