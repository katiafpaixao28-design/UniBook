# DIRETIVAS DO AGENTE DE DESENVOLVIMENTO (METODOLOGIA SDD)
1. FONTE DA VERDADE: Siga rigorosamente as regras em `AGENTS.md` e a tarefa atual em `docs/tasks/*.md`.
2. PROIBIDO INVENTAR: Não implemente rotas, models, campos ou regras que não estejam documentadas na especificação.
3. CONTEXTO MODULAR: Trabalhe em um único arquivo ou módulo por vez. Peça autorização humana antes de avançar.
4. TESTES OBRIGATÓRIOS: Nenhuma entrega é válida se não houver um arquivo de teste funcional correspondente em `tests/`.
5. STACK PADRÃO: Use estritamente Python 3.13, FastAPI, SQLAlchemy 2 (síncrono), Pydantic 2, Ruff e Mypy.
6. RETORNO DE ERROS: Siga o padrão RFC 9457 (Problem Details) para respostas de erro estruturadas.
7. SEGURANÇA PRIMEIRO: Nunca faça commit de senhas, chaves ou segredos. Sempre use variáveis de ambiente ou o Secrets Manager.