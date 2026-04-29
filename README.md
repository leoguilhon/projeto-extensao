# LendoJuntos

Aplicação web desenvolvida como Projeto de Extensão com o objetivo de apoiar a organização de clubes de leitura, centralizando informações sobre membros, livros, encontros e interações em uma única plataforma.

## Objetivo do projeto

O LendoJuntos busca oferecer uma solução simples e organizada para clubes do livro que hoje dependem de ferramentas genéricas, como grupos de mensagens, planilhas e redes sociais, para conduzir suas atividades. A proposta é reunir, em um único sistema, funcionalidades voltadas à criação de clubes, gerenciamento de leituras, organização de encontros e acompanhamento das interações entre participantes.

## Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI
- Banco de dados: PostgreSQL
- Autenticação: JWT

## Estrutura do projeto

```txt
lendojuntos/
├── frontend/   # interface da aplicação
├── backend/    # API e regras de negócio
├── docs/       # documentação acadêmica e artefatos de modelagem
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Estrutura das principais pastas

### Frontend
Responsável pela interface da aplicação, navegação entre páginas e consumo da API.

### Backend
Responsável pelas regras de negócio, autenticação, validação de dados e comunicação com o banco.

### Docs
Responsável por armazenar documentos acadêmicos, diagramas, matrizes, wireframes e demais artefatos do projeto.

## Funcionalidades previstas no MVP

- cadastro e autenticação de usuários
- criação e gerenciamento de clubes de leitura
- ingresso de usuários em clubes
- cadastro e organização de livros por clube
- registro de encontros
- visualização de histórico de leituras
- comentários simples sobre livros ou discussões

## Requisitos para execução

Antes de iniciar, é necessário ter instalado no ambiente:

- Node.js
- Python 3
- Docker Desktop
- Git

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd projeto-extensao
```

### 2. Subir o banco de dados

Na raiz do projeto:

```bash
docker compose up -d
```

### 3. Rodar o frontend

Abra um terminal na raiz do projeto e execute:

```bash
cd frontend
npm install
npm run dev
```

O frontend ficará disponível, em geral, em:

```txt
http://localhost:5173
```

### 4. Rodar o backend

Abra outro terminal na raiz do projeto e execute:

```bash
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API ficará disponível em:

```txt
http://127.0.0.1:8000
```

Documentação automática da API:

```txt
http://127.0.0.1:8000/docs
```

### 5. Rodar frontend e backend ao mesmo tempo

Para executar a aplicação localmente, mantenha dois terminais abertos:

#### Terminal 1 — Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Terminal 2 — Backend
```bash
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Terminal 3 — Banco de dados
Se o banco ainda não estiver rodando:
```bash
docker compose up -d
```

## Variáveis de ambiente

O projeto utiliza um arquivo `.env.example` como referência para configuração inicial.

Exemplo:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/lendojuntos

JWT_SECRET_KEY=trocar_essa_chave
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

VITE_API_BASE_URL=http://localhost:8000
```

## Estado atual do projeto

Até o momento, o projeto conta com:

- estrutura inicial do frontend criada com React, TypeScript e Vite
- estrutura inicial do backend criada com FastAPI
- configuração inicial do PostgreSQL com Docker
- organização inicial do repositório
- definição de documentação e artefatos de modelagem

## Próximos passos

As próximas etapas de desenvolvimento incluem:

- implementação da autenticação
- criação do módulo de clubes
- criação do módulo de livros
- implementação do módulo de encontros
- desenvolvimento do sistema de comentários
- integração entre frontend, backend e banco de dados

## Documentação

A pasta `docs/` reúne os materiais produzidos ao longo do Projeto de Extensão, incluindo:

- cronograma de desenvolvimento
- registro de horas
- diagramas de modelagem
- wireframes
- documentos acadêmicos de acompanhamento

## Autor

Leonardo Guilhon

## Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do Projeto de Extensão.
