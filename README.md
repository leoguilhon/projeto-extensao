# LendoJuntos

Aplicação web desenvolvida como Projeto de Extensão para organização de clubes de leitura.

## Stack
- Frontend: React + TypeScript + Vite
- Backend: FastAPI
- Banco de dados: PostgreSQL
- Autenticação: JWT

## Estrutura
- `frontend/` → interface da aplicação
- `backend/` → API e regras de negócio
- `docs/` → documentação acadêmica e artefatos de modelagem

## Como rodar

### Frontend
```bash
cd frontend
npm install
npm run dev

### Backend
```bash
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
