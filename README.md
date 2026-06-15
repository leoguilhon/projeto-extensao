# LendoJuntos

Aplicacao web desenvolvida como Projeto de Extensao para apoiar a organizacao de clubes do livro em um unico ambiente. O sistema concentra clubes, livros, encontros, confirmacoes de presenca, comentarios e historico de leitura.

## Visao geral

O MVP foi pensado para grupos que hoje dependem de conversas dispersas, planilhas e redes sociais genericas para organizar leituras coletivas. O foco do projeto e oferecer uma experiencia simples para:

- cadastrar e autenticar usuarios
- criar e administrar clubes de leitura
- ingressar em clubes e acompanhar membros
- cadastrar livros e manter apenas uma leitura ativa por clube
- planejar encontros e registrar presencas
- comentar livros e encontros
- consultar historico de leituras concluidas

## Stack atual

- Frontend: React 19 + TypeScript + Vite
- Backend: FastAPI
- Persistencia: PostgreSQL com SQLAlchemy
- Autenticacao: token Bearer opaco com expiracao configuravel
- Empacotamento: Dockerfiles para frontend e backend + `docker-compose.yml`

## Estrutura

```txt
projeto-extensao/
|-- backend/
|   |-- app/
|   |-- tests/
|   |-- Dockerfile
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |-- public/
|   |-- Dockerfile
|   `-- nginx.conf
|-- docs/
|-- .env.example
`-- docker-compose.yml
```

## Como executar localmente

### 1. Banco de dados

```powershell
docker compose up -d postgres
```

O PostgreSQL ficara disponivel em `127.0.0.1:5432` para a rede local e em `postgres:5432` dentro do Docker Compose.

### 2. Backend

```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponivel em `http://127.0.0.1:8000`.

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Interface disponivel em `http://127.0.0.1:5173`.

### 4. Stack completa com Docker

```powershell
docker compose up --build
```

Frontend publicado em `http://127.0.0.1:4173`, backend em `http://127.0.0.1:8000` e PostgreSQL em `127.0.0.1:5432`.

## Variaveis de ambiente

Use `.env.example` como base:

```env
API_TITLE=LendoJuntos API
POSTGRES_DB=lendojuntos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/lendojuntos
ACCESS_TOKEN_EXPIRE_MINUTES=480
ENABLE_SEED_DATA=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173
VITE_API_BASE_URL=http://localhost:8000
```

## Persistencia

Os dados de usuarios, clubes, livros, encontros, comentarios, favoritos, curtidas e tokens de autenticacao agora sao persistidos no PostgreSQL. O backend cria as tabelas automaticamente na inicializacao e, se `ENABLE_SEED_DATA=true`, carrega os dados de demonstracao apenas quando o banco ainda estiver vazio.

## Dados de demonstracao

Quando `ENABLE_SEED_DATA=true`, a API sobe com usuarios e um clube de exemplo. Conta principal:

- E-mail: `ana@lendojuntos.test`
- Senha: `123456`

## Validacao e testes

Comandos utilizados para validacao local:

```powershell
cd frontend
npm run lint
npm run build
```

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
python -m py_compile app\main.py
```

## Documentacao complementar

- Cronograma academico: `docs/academico/`
- Artefatos de modelagem: `docs/artefatos-modelagem/`
- Documentacao tecnica detalhada: [docs/documentacao-tecnica.md](docs/documentacao-tecnica.md)

## Limitacoes do MVP

- O projeto ainda cria o schema automaticamente com SQLAlchemy; nao ha migrations versionadas com Alembic.
- A autenticacao usa token de sessao simples, adequada ao escopo academico do MVP.
- O deploy containerizado depende da instalacao local do Docker.
