# AGENTS.md — Sistema de Gerenciamento de Biblioteca

## 1. Finalidade deste arquivo

Este arquivo é a fonte principal de contexto para agentes e desenvolvedores que trabalhem neste projeto.

Ao implementar ou planejar funcionalidades:

- Respeite as regras de negócio documentadas aqui.
- Não invente regras ausentes. Marque-as como `PENDENTE` e solicite validação.
- Preserve o histórico de empréstimos, multas, reservas, autorizações e alterações cadastrais.
- Prefira soluções simples para o MVP e evite microserviços prematuros.
- Use português nos textos da interface e inglês nos nomes técnicos do código.
- Trate acessibilidade, segurança, auditoria e LGPD como requisitos do produto.

## 2. Visão do produto

O produto será um sistema web de gerenciamento de biblioteca, inicialmente hospedado na AWS. Ele atenderá a equipe da biblioteca, alunos, professores, diretor e coordenadores de curso.

O sistema deverá administrar:

- Catálogo bibliográfico.
- Autores, editoras, assuntos, CDD e Cutter.
- Exemplares físicos.
- Impressão de etiquetas.
- Usuários e perfis.
- Empréstimos, devoluções e renovações.
- Reservas e fila de espera.
- Multas e bloqueios.
- Autorizações excepcionais.
- Descarte e reativação de livros e exemplares.
- Solicitações de aquisição.
- Relatórios e auditoria.

Sistemas de referência funcional: Pergamum e SophiA Biblioteca. Eles devem servir apenas como referência de fluxos; não é objetivo reproduzir todo o escopo desses produtos no MVP.

## 3. Estratégia técnica

### 3.1 Arquitetura da aplicação

Começar com um monólito modular. Cada módulo deve possuir limites claros de responsabilidade para permitir extração futura, se houver necessidade real.

Módulos iniciais:

- `identity`: autenticação, usuários, perfis e permissões.
- `catalog`: livros, autores, editoras, assuntos, CDD e Cutter.
- `inventory`: exemplares, códigos, etiquetas e estados físicos.
- `circulation`: empréstimos, devoluções, renovações, multas e autorizações.
- `reservation`: reservas, fila e expiração.
- `acquisition`: solicitações de aquisição e aprovação.
- `reporting`: consultas, relatórios e exportações.
- `audit`: registro de ações sensíveis.

Não iniciar com Kubernetes, EKS ou microserviços. ECS Fargate é suficiente para o cenário inicial.

### 3.2 Stack planejada

Backend:

- Python 3.13 ou superior, em versão estável suportada pelo projeto.
- FastAPI.
- Uvicorn como servidor ASGI.
- Pydantic 2 e `pydantic-settings` para schemas, validação e configuração.
- API REST com contrato OpenAPI gerado pelo FastAPI.
- SQLAlchemy 2 para persistência.
- Psycopg 3 como driver PostgreSQL.
- Alembic para migrations.
- PostgreSQL.
- `pyproject.toml` como fonte de configuração e dependências.
- `uv` para gerenciamento de dependências, ambiente virtual e lockfile.
- Pytest, pytest-cov e Testcontainers.
- Ruff para lint e formatação.
- Mypy para verificação estática de tipos.

Usar SQLAlchemy síncrono no MVP, salvo necessidade comprovada de acesso assíncrono ao banco. Não misturar sessões síncronas e assíncronas dentro do mesmo módulo.

Frontend:

- TypeScript com modo estrito.
- React, em versão estável suportada pelo projeto.
- SCSS.
- Componentes funcionais e Hooks.
- Formulários implementados com padrões adequados ao React, com validação explícita no cliente.
- Componentes acessíveis e responsivos.
- Proteção de rotas e ações baseada em permissões.
- Organizar a aplicação por páginas/funcionalidades, mantendo componentes específicos próximos da página que os utiliza e componentes reutilizáveis em uma área compartilhada (`shared`).

As versões representam a linha de base do planejamento. Antes de iniciar o projeto, confirmar versões estáveis e compatibilidade. Não realizar upgrade de versão major sem validação explícita.

### 3.3 Infraestrutura AWS

- S3 e CloudFront para o frontend React.
- ECS Fargate para a API Python/FastAPI em container.
- Application Load Balancer para entrada da API.
- RDS PostgreSQL para dados relacionais.
- Cognito para autenticação e recuperação de senha.
- SES para notificações por e-mail.
- SQS para processamento assíncrono de notificações.
- S3 para etiquetas e relatórios gerados, quando for necessário armazená-los.
- CloudWatch para logs, métricas e alertas.
- Secrets Manager para segredos e credenciais.
- Route 53 e ACM para domínio e HTTPS.
- Infraestrutura como código com Terraform ou AWS CDK; escolher uma opção no início.

Manter ambientes separados de desenvolvimento, homologação e produção.

## 4. Conceitos principais do domínio

### 4.1 Livro

Representa a obra ou edição bibliográfica cadastrada. O ISBN identifica o registro bibliográfico, não uma unidade física individual.

### 4.2 Exemplar

Representa uma unidade física emprestável. Vários exemplares podem pertencer ao mesmo livro e compartilhar o mesmo ISBN.

Cada exemplar deve possuir um identificador interno exclusivo, como número de tombo ou código de barras. Essa identificação é obrigatória tecnicamente, pois o ISBN sozinho não permite saber qual unidade foi emprestada, perdida, danificada ou descartada.

### 4.3 Usuário da biblioteca

Pessoa que pode consultar o catálogo e, conforme seu perfil, realizar empréstimos, renovações e reservas.

Perfis iniciais:

- Aluno.
- Professor.
- Bibliotecário.
- Estagiário.
- Diretor.
- Coordenador de curso.
- Administrador técnico.

## 5. Regras de cadastro bibliográfico

### 5.1 Campos obrigatórios

- Título.
- ISBN.
- Editora.
- Pelo menos um autor.

### 5.2 Campos opcionais informados na entrevista

- Edição.
- Número de páginas.

### 5.3 Campos complementares necessários

- Assuntos.
- CDD ou número de classificação.
- Cutter.
- Ano de publicação.

O ano de publicação é necessário para a etiqueta, mas sua obrigatoriedade no cadastro ainda está `PENDENTE` de confirmação.

### 5.4 ISBN

- É obrigatório.
- Um livro não pode ser cadastrado sem ISBN.
- Não pode existir ISBN duplicado no catálogo.
- Aceitar e validar ISBN-10 e ISBN-13, se ambos forem usados pela instituição.
- Normalizar o ISBN antes de validar unicidade, removendo espaços e hífens.
- Preservar uma versão formatada apenas para apresentação.

### 5.5 Autores

- Um livro pode possuir vários autores.
- Um autor pode estar associado a vários livros.
- A ordem dos autores deve ser preservada.
- A interface deve permitir adicionar e remover campos de autor dinamicamente.

### 5.6 Classificação

- CDD, Cutter e assuntos devem auxiliar a pesquisa e a organização física.
- Apenas o bibliotecário pode alterar CDD e Cutter.
- Alterações de classificação devem entrar na auditoria.

## 6. Exemplares e etiquetas

### 6.1 Criação de exemplares

- O cadastro do livro deve permitir informar a quantidade inicial de exemplares.
- Ao informar uma quantidade, o sistema deve criar os exemplares automaticamente.
- Todos os exemplares compartilham o ISBN do livro.
- Cada exemplar recebe um código interno exclusivo.
- Também deve ser possível adicionar novos exemplares posteriormente.

### 6.2 Estados do exemplar

Estados iniciais sugeridos:

- `AVAILABLE`: disponível.
- `LOANED`: emprestado.
- `ON_HOLD`: separado para uma reserva.
- `LOST`: perdido.
- `DAMAGED`: danificado.
- `DISCARDED`: descartado.

Transições de estado devem ser validadas pelo domínio. Um exemplar descartado não pode ser emprestado, mas pode ser reativado por usuário autorizado.

### 6.3 Conteúdo da etiqueta

A etiqueta deve conter:

1. Número de classificação, indicando o assunto da obra. Exemplo: `005.1` para Computação.
2. Identificação do autor pelo padrão Cutter: primeira letra do sobrenome, número correspondente e primeira letra do título. Exemplo: `M 722 T`.
3. Edição. Exemplo: `4. ed.`.
4. Ano de publicação. Exemplo: `2008`.
5. Número do exemplar. Exemplo: `e.2`.

Depois do cadastro, o sistema deve gerar as etiquetas para impressão. Também deve permitir reimpressão posterior.

Formato, dimensões, margens, quantidade por folha e modelo de impressora estão `PENDENTES`.

## 7. Papéis e permissões

| Operação | Bibliotecário | Estagiário | Diretor | Aluno/Professor | Coordenador |
| --- | --- | --- | --- | --- | --- |
| Cadastrar livro | Sim | Sim | Não | Não | Não |
| Alterar dados bibliográficos comuns | Sim | Sim | Não | Não | Não |
| Alterar CDD e Cutter | Sim | Não | Não | Não | Não |
| Adicionar exemplares | Sim | Sim | Não | Não | Não |
| Descartar ou excluir logicamente | Sim | Não | Não | Não | Não |
| Reativar item descartado | Sim | Não | Não | Não | Não |
| Registrar empréstimo e devolução | Sim | Sim | Não | Não | Não |
| Registrar autorização excepcional | Sim | Sim | Autoriza externamente | Não | Não |
| Renovar pelo portal | Não | Não | Não | Sim | Não |
| Reservar pelo portal | Não | Não | Não | Sim | Não |
| Solicitar aquisição | Sim | Não | Não | Não | Não |
| Avaliar solicitação de aquisição | Não | Não | Não | Não | Sim |

O administrador técnico gerencia contas, perfis e configurações, mas não deve receber automaticamente permissão para executar operações bibliotecárias.

## 8. Empréstimos

### 8.1 Limites e prazos

| Perfil | Limite padrão | Prazo | Renovações máximas |
| --- | ---: | ---: | ---: |
| Aluno | 3 exemplares ativos | 7 dias úteis | 2 |
| Professor | 4 exemplares ativos | 7 dias úteis | 2 |

### 8.2 Cálculo de prazo

- O prazo deve considerar dias úteis.
- Sábados e domingos não contam.
- O tratamento de feriados está `PENDENTE`.
- A data limite deve ser calculada no fuso horário configurado para a instituição.
- Datas e instantes técnicos devem ser armazenados de forma consistente, preferencialmente em UTC.
- A política de calendário deve ser configurável e não espalhada pelo código.

### 8.3 Renovação

- Cada renovação adiciona mais 7 dias úteis.
- São permitidas no máximo 2 renovações por empréstimo.
- A renovação pode ocorrer presencialmente ou pelo portal do usuário.
- A regra para renovação quando existe fila de reserva está `PENDENTE`. Não presumir comportamento sem validação.

### 8.4 Limite excepcional

Alunos e professores podem ultrapassar o limite apenas com autorização do diretor.

A comunicação com o diretor ocorre diretamente, fora do sistema. Portanto, o MVP não precisa implementar caixa de entrada, notificação ou fluxo digital de aprovação para o diretor.

O atendente deverá registrar no sistema:

- Que houve autorização.
- Diretor responsável.
- Data e hora.
- Quantidade adicional autorizada.
- Motivo ou observação, se informado.
- Usuário que registrou a autorização.

O sistema nunca deve aumentar silenciosamente o limite.

### 8.5 Concorrência

- Um exemplar só pode possuir um empréstimo ativo.
- A operação de empréstimo deve ser transacional.
- Implementar controle de concorrência para impedir que dois atendentes emprestem o mesmo exemplar simultaneamente.

## 9. Atrasos, multas e bloqueios

- Devoluções após a data limite geram multa.
- Usuário com multa pendente não pode realizar novos empréstimos.
- O bloqueio permanece até o pagamento ou baixa da multa.
- Empréstimos e histórico do usuário continuam consultáveis durante o bloqueio.
- A fórmula ou valor da multa está `PENDENTE`.
- A forma de pagamento está `PENDENTE`.
- Até definição contrária, o sistema apenas registra a quitação; não implementar gateway de pagamento.
- Cancelamento, desconto ou baixa manual de multa devem exigir permissão e gerar auditoria.
- Valores monetários devem usar tipo decimal, nunca ponto flutuante.

Entidades sugeridas:

- `Fine`: multa gerada por um empréstimo atrasado.
- `FineSettlement`: pagamento, cancelamento ou baixa administrativa.
- `LoanPolicy`: limites, prazos e quantidade de renovações.
- `FinePolicy`: parâmetros de cálculo da multa.

## 10. Reservas

- Deve ser possível reservar um livro mesmo quando todos os exemplares estiverem emprestados.
- As reservas devem formar uma fila por ordem de criação.
- Quando um exemplar ficar disponível, o primeiro usuário elegível da fila recebe prioridade.
- A reserva dura 1 dia.

Permanece `PENDENTE` confirmar:

- Se o prazo de 1 dia começa na criação da reserva ou quando o exemplar fica disponível.
- Se o prazo usa dia útil ou corrido.
- Se uma reserva ativa impede renovação do empréstimo atual.
- Quais canais de notificação serão usados.

Até a confirmação, não codificar regras definitivas para esses pontos.

Estados sugeridos:

- `WAITING`: aguardando exemplar.
- `READY_FOR_PICKUP`: exemplar separado.
- `FULFILLED`: reserva atendida.
- `EXPIRED`: prazo expirado.
- `CANCELLED`: cancelada pelo usuário ou atendente.

## 11. Descarte, exclusão e reativação

- Apenas o bibliotecário pode excluir ou descartar livros e exemplares.
- A exclusão deve ser lógica; não apagar fisicamente registros com histórico.
- Um item descartado deixa de estar disponível para pesquisa operacional, reserva e empréstimo.
- O histórico continua disponível para usuários autorizados.
- Livros e exemplares descartados podem ser reativados.
- Descarte e reativação devem registrar usuário, data, motivo e estado anterior.
- Um exemplar com empréstimo ativo pode ser marcado para descarte, mas o empréstimo não deve desaparecer.
- O comportamento final do exemplar após a devolução deve respeitar a marcação de descarte.

## 12. Solicitações de aquisição

- O bibliotecário pode solicitar livros ao coordenador do curso.
- O coordenador pode aprovar, rejeitar ou solicitar ajustes.
- O sistema deve guardar solicitante, curso, livro desejado, justificativa, status, datas e comentários.
- O orçamento é definido no momento da aprovação, fora do escopo do sistema.
- Não implementar cálculo, reserva, limite ou controle orçamentário.
- Não exigir valor financeiro na solicitação ou aprovação, salvo mudança futura de requisito.

Estados sugeridos:

- `DRAFT`.
- `SUBMITTED`.
- `NEEDS_CHANGES`.
- `APPROVED`.
- `REJECTED`.
- `CANCELLED`.

## 13. Modelo de dados inicial

Entidades principais:

- `Book`
- `Author`
- `BookAuthor`
- `Publisher`
- `Subject`
- `BookSubject`
- `Copy`
- `Member`
- `Role`
- `Permission`
- `Loan`
- `Reservation`
- `LimitAuthorization`
- `Fine`
- `FineSettlement`
- `LoanPolicy`
- `FinePolicy`
- `AcquisitionRequest`
- `AuditLog`

Restrições mínimas:

- ISBN normalizado com índice único.
- Código de exemplar com índice único.
- Pelo menos um autor por livro.
- No máximo um empréstimo ativo por exemplar.
- Contagem de renovações nunca negativa e nunca acima da política vigente.
- Valores de multa nunca negativos.
- Operações sensíveis vinculadas ao usuário responsável.

## 14. Fluxos principais

### 14.1 Cadastro e etiquetagem

1. Bibliotecário ou estagiário informa os dados bibliográficos.
2. O sistema valida campos obrigatórios e unicidade do ISBN.
3. O usuário adiciona um ou mais autores.
4. O bibliotecário informa ou revisa CDD e Cutter.
5. O usuário informa a quantidade de exemplares.
6. O sistema cria códigos individuais.
7. O sistema gera etiquetas para impressão.

O estagiário pode preencher dados comuns, mas não pode alterar CDD e Cutter.

### 14.2 Empréstimo

1. Atendente identifica o usuário.
2. Atendente identifica o exemplar pelo código exclusivo.
3. O sistema verifica disponibilidade, bloqueios, multas e limite vigente.
4. Se houver excesso de limite, o atendente deve registrar autorização do diretor.
5. O sistema calcula a devolução em 7 dias úteis.
6. O empréstimo é confirmado de forma transacional.

### 14.3 Devolução e multa

1. Atendente identifica o exemplar.
2. O sistema encerra o empréstimo.
3. Se houver atraso, calcula ou registra a multa conforme política vigente.
4. Enquanto a multa permanecer aberta, novos empréstimos ficam bloqueados.
5. O sistema verifica a fila de reserva antes de disponibilizar o exemplar.

### 14.4 Descarte e reativação

1. Bibliotecário seleciona o livro ou exemplar.
2. Informa o motivo.
3. O sistema registra o descarte lógico.
4. O item deixa de participar da circulação.
5. Se necessário, o bibliotecário pode reativá-lo posteriormente.
6. Toda a sequência permanece auditável.

## 15. Requisitos de pesquisa

A pesquisa deve permitir, no mínimo:

- Título.
- Autor.
- ISBN.
- Editora.
- Assunto.
- CDD.
- Cutter.
- Disponibilidade.

Os resultados devem indicar quantidade total, quantidade disponível e situação das reservas, sem expor dados pessoais de quem está com o exemplar.

## 16. API e padrões de implementação

- Adotar API REST versionada, por exemplo `/api/v1`.
- Gerar e manter contrato OpenAPI.
- Usar schemas Pydantic nas bordas da aplicação; não expor modelos SQLAlchemy diretamente.
- Aplicar validações também no backend, mesmo quando existirem no frontend.
- Retornar erros em formato consistente, preferencialmente Problem Details.
- Usar paginação em pesquisas e listagens.
- Evitar regras de domínio nas funções de rota do FastAPI.
- Usar dependências do FastAPI para autenticação, autorização, sessão de banco e contexto da requisição.
- Manter as rotas finas; regras de negócio devem permanecer nos serviços e objetos do domínio.
- Usar type hints em todo código de produção e schemas Pydantic para entrada e saída.
- Organizar o backend por funcionalidade, evitando uma única pasta global de `models`, `services` ou `routers` para todos os módulos.
- Usar transações nos fluxos de circulação, reserva, multa e descarte.
- Utilizar migrations; não depender de geração automática de schema em produção.
- Nunca armazenar senha no banco da aplicação quando a autenticação estiver no Cognito.
- Aplicar idempotência onde repetição de requisição puder duplicar operações.

## 17. Segurança, LGPD e auditoria

- Todo tráfego externo deve usar HTTPS.
- Aplicar menor privilégio em permissões da aplicação e da AWS.
- Não registrar senhas, tokens ou dados pessoais sensíveis em logs.
- Criptografar dados em trânsito e em repouso.
- Configurar backup e recuperação pontual do banco.
- Definir política de retenção de logs e dados.
- Registrar alterações de ISBN, classificação, descarte, reativação, multa, autorização e permissões.
- A auditoria deve guardar ator, ação, data, entidade afetada e mudanças relevantes.
- Operações históricas não devem depender do nome atual do usuário para preservar contexto.

## 18. Estratégia de testes

### 18.1 Testes unitários

Cobrir principalmente:

- Validação e normalização de ISBN.
- Cálculo de 7 dias úteis.
- Limite por perfil.
- Duas renovações máximas.
- Bloqueio por multa.
- Autorização excepcional.
- Fila de reservas.
- Regras de descarte e reativação.

### 18.2 Testes de integração

- PostgreSQL real via Testcontainers.
- Constraints e migrations.
- Concorrência de empréstimos.
- Transações de devolução, multa e reserva.
- Autorização por perfil.
- Testes da API com `httpx` e o cliente ASGI do FastAPI.

### 18.3 Testes end-to-end

- Cadastro completo e impressão de etiqueta.
- Empréstimo e devolução sem atraso.
- Devolução com multa e bloqueio.
- Renovação presencial e pelo portal.
- Reserva, fila e atendimento.
- Descarte e reativação.
- Solicitação e aprovação de aquisição.

## 19. Critérios de aceite do MVP

- ISBN inválido ou duplicado é rejeitado.
- Um cadastro com cinco unidades cria cinco exemplares identificáveis.
- O estagiário altera dados comuns, mas não CDD ou Cutter.
- Apenas o bibliotecário descarta e reativa itens.
- Aluno possui limite padrão de 3 empréstimos ativos.
- Professor possui limite padrão de 4 empréstimos ativos.
- A devolução é calculada em 7 dias úteis para ambos os perfis.
- Cada empréstimo permite no máximo 2 renovações.
- Excesso de limite exige registro da autorização direta do diretor.
- Atraso gera multa conforme política configurada.
- Multa pendente bloqueia novos empréstimos.
- Exclusão lógica preserva todo o histórico.
- Etiquetas podem ser geradas e reimpressas.
- Reservas respeitam a ordem da fila.
- Operações sensíveis ficam registradas na auditoria.

## 20. Roadmap inicial

| Etapa | Estimativa | Entrega |
| --- | ---: | --- |
| Descoberta | 1 semana | Validação das pendências e protótipos |
| Fundação técnica | 1–2 semanas | Repositórios, autenticação, CI/CD e AWS |
| Catálogo | 2 semanas | Livros, autores, assuntos, ISBN e pesquisa |
| Exemplares e etiquetas | 1–2 semanas | Criação em lote, códigos e impressão |
| Circulação | 3 semanas | Empréstimos, devoluções, renovações, multas e limites |
| Reservas | 1–2 semanas | Fila, expiração e notificações |
| Aquisições e relatórios | 1 semana | Solicitações e relatórios básicos |
| Piloto | 1–2 semanas | Testes, correções, treinamento e produção |

Estimativa total para equipe pequena: 12–14 semanas. Para uma pessoa desenvolvedora trabalhando sozinha, considerar aproximadamente 20–24 semanas.

## 21. Decisões ainda pendentes

Não implementar uma decisão definitiva para estes itens sem nova validação:

- Valor ou fórmula da multa.
- Se a multa considera dias corridos ou úteis.
- Forma de pagamento e de confirmação da quitação.
- Tratamento de feriados no prazo de empréstimo.
- Comportamento da renovação quando existe reserva.
- Momento inicial do prazo de 1 dia da reserva.
- Se o dia da reserva é útil ou corrido.
- Canais de notificação.
- Obrigatoriedade do ano de publicação.
- Dimensões e layout físico das etiquetas.
- Modelo de impressora e tipo de papel.
- Origem dos cadastros de alunos e professores.
- Necessidade de importação MARC21.
- Política para livros sem ISBN em acervo legado. Novos cadastros sempre exigem ISBN.

## 22. Fora do escopo inicial

- Controle orçamentário de aquisições.
- Gateway de pagamento de multas.
- Fluxo digital de aprovação do diretor.
- Aplicativo móvel nativo.
- Microserviços e Kubernetes.
- Integração contábil.
- Autocompra de livros aprovados.
- Funcionalidades não confirmadas apenas porque existem no Pergamum ou SophiA.

## 23. Estrutura do projeto e convenções arquiteturais

Esta seção define onde cada tipo de código deve ser colocado. Ao criar novas funcionalidades, preservar esta organização e evitar pastas globais que misturem responsabilidades de domínios diferentes.

### 23.1 Estrutura geral do repositório

```text
Unibook/
├── frontend/                           # Aplicação web React
│   ├── src/
│   │   ├── pages/                     # Páginas e funcionalidades de nível de rota
│   │   │   ├── catalog/
│   │   │   │   ├── components/        # Componentes exclusivos do catálogo
│   │   │   │   ├── hooks/             # Hooks exclusivos do catálogo
│   │   │   │   ├── catalog-page.tsx
│   │   │   │   └── catalog-page.scss
│   │   │   ├── circulation/
│   │   │   ├── reservations/
│   │   │   ├── acquisitions/
│   │   │   ├── users/
│   │   │   ├── reports/
│   │   │   └── audit/
│   │   │
│   │   ├── shared/                    # Recursos reutilizáveis entre páginas
│   │   │   ├── components/            # Componentes genéricos de UI
│   │   │   ├── hooks/                 # Hooks React reutilizáveis
│   │   │   ├── services/
│   │   │   │   └── api/               # Infraestrutura do cliente REST
│   │   │   ├── types/                 # Tipos TypeScript compartilhados
│   │   │   ├── utils/                 # Utilitários genéricos
│   │   │   └── assets/                # Imagens, ícones e logos importados
│   │   │
│   │   ├── auth/                      # Autenticação/autorização no frontend
│   │   │   ├── auth-context.tsx
│   │   │   ├── protected-route.tsx
│   │   │   └── permissions.ts
│   │   │
│   │   ├── routes/
│   │   │   └── router.tsx             # Definição das rotas
│   │   │
│   │   ├── app.tsx                    # Componente raiz React
│   │   ├── app.scss                   # Estilos do componente raiz
│   │   └── main.tsx                   # Bootstrap da aplicação
│   │
│   ├── public/
│   │   └── favicon.ico
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── backend/                            # Monólito modular Python/FastAPI
│   ├── app/
│   │   ├── main.py                    # Entrada da aplicação FastAPI
│   │   │
│   │   ├── core/                      # Infraestrutura transversal
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── permissions.py
│   │   │   ├── errors.py
│   │   │   ├── pagination.py
│   │   │   ├── logging.py
│   │   │   └── time.py
│   │   │
│   │   ├── modules/
│   │   │   ├── identity/
│   │   │   ├── catalog/
│   │   │   ├── inventory/
│   │   │   ├── circulation/
│   │   │   ├── reservation/
│   │   │   ├── acquisition/
│   │   │   ├── reporting/
│   │   │   └── audit/
│   │   │
│   │   ├── integrations/
│   │   │   ├── cognito/
│   │   │   ├── s3/
│   │   │   ├── ses/
│   │   │   └── sqs/
│   │   │
│   │   └── api/
│   │       └── v1/
│   │           └── router.py           # Agrega os routers dos módulos
│   │
│   ├── migrations/
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   │
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile
│   └── README.md
│
├── e2e/                                # Testes de ponta a ponta do sistema
│   ├── catalog/
│   ├── circulation/
│   ├── reservations/
│   ├── disposal/
│   └── acquisitions/
│
├── infrastructure/                     # Infraestrutura como código
│   ├── environments/
│   │   ├── development/
│   │   ├── staging/
│   │   └── production/
│   └── modules/
│       ├── networking/
│       ├── frontend/
│       ├── api/
│       ├── database/
│       ├── authentication/
│       ├── messaging/
│       ├── storage/
│       └── observability/
│
├── docs/
│   ├── architecture/
│   ├── domain/
│   ├── api/
│   └── adr/                            # Architecture Decision Records
│
├── scripts/
├── .github/
│   └── workflows/
│       ├── frontend-ci.yml
│       ├── backend-ci.yml
│       └── deploy.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

Pastas e arquivos adicionais podem ser criados quando houver necessidade real, desde que respeitem os limites de responsabilidade definidos aqui.

### 23.2 Organização do frontend React

O frontend deve ser organizado principalmente por página ou funcionalidade.

Regras:

- Usar componentes funcionais.
- Usar Hooks para estado, efeitos e comportamento React reutilizável.
- Componentes usados apenas por uma página devem permanecer dentro de `pages/<feature>/components/`.
- Hooks usados apenas por uma página devem permanecer dentro de `pages/<feature>/hooks/`.
- Componentes genéricos reutilizados entre funcionalidades devem ficar em `shared/components/`.
- Hooks reutilizáveis devem ficar em `shared/hooks/`.
- Tipos compartilhados do frontend devem ficar em `shared/types/`.
- Utilitários genéricos devem ficar em `shared/utils/`.
- A infraestrutura de comunicação com a API deve ficar em `shared/services/api/`.
- Assets importados pelo código devem ficar em `shared/assets/`.
- Arquivos estáticos servidos diretamente, como `favicon.ico`, devem ficar em `public/`.
- Não mover um componente para `shared` apenas por possibilidade futura de reutilização. Fazer isso quando houver reutilização real ou quando o componente for intencionalmente genérico.
- `shared/` não deve importar código de `pages/`.

Exemplo de uma página:

```text
pages/
└── catalog/
    ├── components/
    │   ├── book-card/
    │   │   ├── book-card.tsx
    │   │   └── book-card.scss
    │   ├── book-filter/
    │   └── availability-badge/
    ├── hooks/
    │   └── use-catalog.ts
    ├── catalog-page.tsx
    └── catalog-page.scss
```

Direção esperada das dependências do frontend:

```text
app.tsx / routes
    ├── pages
    │   ├── auth
    │   └── shared
    ├── auth
    │   └── shared
    └── shared
```

Nunca permitir dependência de `shared` para uma página específica.

### 23.3 Autenticação e autorização no frontend

A pasta `frontend/src/auth/` concentra as preocupações React relacionadas a autenticação e autorização.

Responsabilidades esperadas:

- Contexto ou provider de autenticação.
- Integração da sessão com Cognito.
- Proteção de rotas.
- Helpers para verificar permissões.
- Controle de visibilidade de ações de UI conforme as permissões.

A proteção no frontend serve para experiência do usuário, mas nunca substitui autorização no backend. Toda operação protegida deve validar a permissão novamente na API.

### 23.4 Organização interna dos módulos do backend

Cada módulo de negócio deve possuir seus próprios arquivos técnicos. Evitar uma pasta global única de `models`, `services`, `repositories` ou `routers` para todos os domínios.

Estrutura de referência:

```text
modules/
└── circulation/
    ├── router.py
    ├── schemas.py
    ├── models.py
    ├── repository.py
    ├── service.py
    ├── domain.py
    └── permissions.py
```

Responsabilidades:

- `router.py`: camada HTTP; rotas, dependências, autenticação/autorização e mapeamento de request/response.
- `schemas.py`: schemas Pydantic de entrada e saída.
- `service.py`: casos de uso e coordenação da operação.
- `domain.py`: regras de negócio e validações de domínio.
- `repository.py`: acesso à persistência e consultas SQLAlchemy.
- `models.py`: modelos SQLAlchemy pertencentes ao módulo.
- `permissions.py`: regras/permissões específicas do módulo quando necessário.

Fluxo normal:

```text
HTTP Request
    ↓
router.py
    ↓
service.py
    ├── domain.py
    └── repository.py
            ↓
        models.py
            ↓
        PostgreSQL
```

Não colocar regras de negócio relevantes em `router.py`.

### 23.5 Dependências entre módulos do backend

Evitar imports arbitrários de implementações internas entre módulos.

Preferir:

```text
módulo A
    ↓
interface/serviço público do módulo B
    ↓
módulo B
```

Evitar dependências como:

```text
catalog.models importado diretamente por vários módulos
circulation.models usado como API pública
repository de reservation chamado por módulos sem relação direta
```

Um módulo deve expor apenas o mínimo necessário para outros módulos.

Esse limite existe para reduzir acoplamento e permitir extração futura de um módulo caso exista necessidade real, sem transformar o MVP em microserviços prematuramente.

### 23.6 `core` e `integrations`

`backend/app/core/` contém infraestrutura transversal à aplicação e não regras específicas de um domínio.

Exemplos:

- Configuração da aplicação.
- Engine e sessão do banco.
- Primitivas de autenticação/autorização.
- Tratamento global de erros.
- Paginação.
- Logging.
- Utilitários de data/hora e UTC.

`backend/app/integrations/` contém adaptadores para serviços externos:

- Cognito.
- S3.
- SES.
- SQS.

Módulos de negócio não devem espalhar chamadas diretas aos SDKs externos quando uma integração/adaptador pode encapsular esse comportamento.

### 23.7 Rotas e contrato da API

A API deve usar o prefixo:

```text
/api/v1
```

`backend/app/api/v1/router.py` deve agregar os routers públicos dos módulos.

Exemplos esperados:

```text
/api/v1/auth/
/api/v1/users/
/api/v1/books/
/api/v1/authors/
/api/v1/publishers/
/api/v1/subjects/
/api/v1/copies/
/api/v1/loans/
/api/v1/returns/
/api/v1/renewals/
/api/v1/fines/
/api/v1/reservations/
/api/v1/acquisition-requests/
/api/v1/reports/
/api/v1/audit/
```

Esses caminhos são referências arquiteturais e podem ser refinados durante a implementação, desde que o contrato continue REST, versionado e coerente com os módulos do domínio.

### 23.8 Persistência e limites transacionais

Usar SQLAlchemy síncrono no MVP conforme definido anteriormente.

Operações compostas devem possuir limites transacionais claros, principalmente:

- Empréstimo.
- Devolução.
- Renovação quando houver efeitos relacionados.
- Reserva.
- Geração ou baixa de multa.
- Descarte.
- Reativação.

Em um empréstimo, por exemplo, validação, controle de concorrência, criação do empréstimo, alteração do estado do exemplar e auditoria devem ser coordenados de forma que uma falha não deixe o sistema em estado parcialmente atualizado.

Constraints importantes devem ser aplicadas também no banco quando possível, incluindo:

- ISBN normalizado único.
- Código de exemplar único.
- No máximo um empréstimo ativo por exemplar.
- Valores de multa não negativos.
- Operações sensíveis associadas ao ator responsável.

### 23.9 Configuração e segredos

Configuração do backend deve usar variáveis de ambiente e `pydantic-settings`.

Manter `.env.example` sem segredos reais.

Exemplos de configuração:

```text
APP_ENV=
DATABASE_URL=
AWS_REGION=
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
S3_BUCKET=
SQS_QUEUE_URL=
SES_FROM_EMAIL=
```

Nunca commitar:

- Senhas.
- Tokens.
- Chaves AWS.
- Credenciais de banco.
- Segredos de aplicações externas.

Em produção, segredos devem ser fornecidos por AWS Secrets Manager ou mecanismo equivalente aprovado.

### 23.10 Desenvolvimento local

Usar `docker-compose.yml` para dependências locais quando necessário, principalmente PostgreSQL.

Fluxo esperado de desenvolvimento:

```text
React dev server
        ↓
FastAPI / Uvicorn
        ↓
PostgreSQL local/container
```

O frontend e o backend devem permanecer executáveis independentemente durante desenvolvimento.

O backend usa:

```text
pyproject.toml
uv.lock
uv
```

como base de dependências e ambiente Python.

### 23.11 Infraestrutura como código

A infraestrutura deve ser definida com **Terraform ou AWS CDK**. A escolha permanece pendente e deve ser registrada antes da implementação.

Separar configurações por ambiente:

```text
infrastructure/
└── environments/
    ├── development/
    ├── staging/
    └── production/
```

Separar componentes reutilizáveis de infraestrutura por responsabilidade, como rede, frontend, API, banco, autenticação, mensageria, storage e observabilidade.

### 23.12 Architecture Decision Records

Decisões técnicas relevantes devem ser documentadas em `docs/adr/`.

Exemplos:

```text
docs/adr/
├── 0001-modular-monolith.md
├── 0002-react-frontend.md
├── 0003-fastapi-backend.md
├── 0004-postgresql.md
├── 0005-cognito-authentication.md
└── 0006-terraform-or-cdk.md
```

Cada ADR deve registrar, no mínimo:

- Contexto.
- Decisão.
- Alternativas consideradas.
- Consequências.
- Status.

Não alterar silenciosamente uma decisão arquitetural consolidada. Mudanças relevantes devem atualizar ou substituir o ADR correspondente.

### 23.13 Testes relacionados à arquitetura

Além da estratégia definida na seção 18:

Frontend deve cobrir, conforme relevância:

- Componentes.
- Hooks com lógica relevante.
- Validação de formulários.
- Proteção de rotas.
- Visibilidade de ações por permissão.
- Integração com o cliente da API em pontos críticos.

Testes end-to-end devem permanecer separados em `e2e/` e cobrir fluxos completos do usuário.

Backend:

- Testes unitários devem privilegiar `domain.py` e serviços com regras de negócio.
- Testes de integração devem validar repositories, constraints, migrations, transações e autorização da API.
- Usar PostgreSQL real via Testcontainers nos testes em que comportamento específico do banco for relevante.

### 23.14 Regras de nomenclatura e idioma

Manter:

- Português para textos exibidos ao usuário.
- Inglês para nomes técnicos do código.
- Inglês para classes, funções, variáveis, entidades, endpoints internos e nomes de arquivos técnicos.

Exemplos de nomes de domínio:

```text
Book
Copy
Loan
Reservation
Fine
FineSettlement
AcquisitionRequest
AuditLog
```

Evitar misturar português e inglês em identificadores técnicos.

### 23.15 Fonte de verdade e conflitos

Este `AGENTS.md` é a principal fonte de contexto do projeto.

Quando existir conflito entre um documento arquitetural antigo e este arquivo:

1. Seguir as regras de negócio e decisões explícitas mais recentes deste `AGENTS.md`.
2. Não assumir que exemplos antigos continuam válidos.
3. Atualizar a documentação arquitetural relacionada quando uma decisão técnica for alterada.
4. Manter itens não confirmados como `PENDENTE`.
5. Não transformar decisões pendentes em comportamento definitivo sem validação.

