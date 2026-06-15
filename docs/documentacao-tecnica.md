# Documentacao Tecnica

## Objetivo

Este documento consolida as decisoes tecnicas da entrega final do projeto LendoJuntos e serve como referencia rapida para execucao, validacao e demonstracao do MVP.

## Arquitetura

- `frontend/`: aplicacao React com rotas protegidas, consumo da API via Axios e telas para clubes, livros, encontros e perfil.
- `backend/app/api/`: definicao das rotas FastAPI.
- `backend/app/services/`: regras de negocio para autenticacao, clubes, livros, encontros, comentarios e usuarios.
- `backend/app/db/models.py`: modelos relacionais persistidos com SQLAlchemy.
- `backend/app/db/session.py`: engine, sessao e inicializacao do schema.
- `backend/tests/`: testes automatizados de regras centrais do backend.

## Persistencia

- banco relacional: PostgreSQL
- ORM: SQLAlchemy 2.x
- driver: `psycopg`
- criacao de schema: `Base.metadata.create_all()` na inicializacao da API
- carga inicial: seed opcional executada apenas quando o banco ainda nao possui usuarios

## Regras de negocio principais

- apenas membros autenticados acessam dados internos de um clube
- apenas administradores podem criar encontros e cadastrar livros
- apenas o criador do clube pode editar ou excluir o proprio clube
- apenas um livro pode permanecer com status `em_leitura` por clube
- encontros podem ser vinculados somente a livros do mesmo clube
- comentarios sao aceitos apenas quando vinculados a livro ou encontro
- ao sair de um clube, o usuario perde suas confirmacoes de presenca nos encontros daquele clube

## Seguranca e validacao

- senhas armazenadas com `PBKDF2-HMAC-SHA256`
- compatibilidade com hashes legados para nao quebrar contas antigas persistidas antes da migracao
- tokens Bearer persistidos em tabela propria com expiracao configuravel por ambiente
- normalizacao de entradas textuais e de e-mail no backend
- rejeicao de campos preenchidos apenas com espacos

## Variaveis de ambiente

| Variavel | Uso |
| --- | --- |
| `API_TITLE` | titulo exibido pela API FastAPI |
| `POSTGRES_DB` | nome do banco usado pelo container PostgreSQL |
| `POSTGRES_USER` | usuario do banco usado pelo container PostgreSQL |
| `POSTGRES_PASSWORD` | senha do banco usada pelo container PostgreSQL |
| `DATABASE_URL` | string de conexao do backend com o PostgreSQL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | tempo de vida do token de sessao |
| `ENABLE_SEED_DATA` | ativa ou desativa carga automatica de dados de demonstracao |
| `CORS_ORIGINS` | lista separada por virgula com origens permitidas |
| `VITE_API_BASE_URL` | URL base usada pelo frontend para chamar a API |

## Fluxo de demonstracao

1. Subir o banco com `docker compose up -d postgres`.
2. Acessar o login com a conta seed `ana@lendojuntos.test / 123456`.
3. Entrar no dashboard e abrir o clube seed.
4. Consultar livro atual, historico, encontros futuros e comentarios.
5. Confirmar presenca em um encontro e publicar um comentario.
6. Como administradora, criar novo encontro ou atualizar o status de um livro.

## Validacao executada

- `npm run lint`
- `npm run build`
- `python -m unittest discover -s backend/tests -v`
- `python -m py_compile` nos modulos Python do backend

## Preparacao para deploy

- `backend/Dockerfile` publica a API com Uvicorn
- `frontend/Dockerfile` gera build estatico com Vite e publica via Nginx
- `frontend/nginx.conf` garante fallback de SPA para o `index.html`
- `docker-compose.yml` orquestra PostgreSQL, backend e frontend com variaveis de ambiente coerentes com o MVP
