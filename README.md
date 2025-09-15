# TCC Auditoria & Conformidade — API (FastAPI)

API mínima (MVP) para o projeto de auditoria e conformidade com IA.

## Stack
- FastAPI + Uvicorn
- SQLAlchemy + Alembic (opcional)
- PostgreSQL
- Qdrant (vetor semântico) — opcional neste MVP (stubado)
- JWT (simples) via `python-jose`

## Rodando com Docker
```bash
docker compose up --build
```

caso não de build
``` bash
docker compose down -v
docker compose up --build
```

A API ficará em http://localhost:8000/docs

Usuário de teste: `admin@local` / senha: `admin`

## Endpoints principais
- `POST /auth/token` — login e emissão de JWT (mock simples)
- `POST /projects` / `GET /projects` — CRUD básico de projetos
- `POST /documents` — upload de documentos (metadados + conteúdo textual)
- `POST /analyses/run` — executa análise simulada de conformidade (stub)
- `GET /reports/{analysis_id}` — obtém resultado resumido

## Variáveis de ambiente (.env)
```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/tcc_auditoria
JWT_SECRET=devsecret
JWT_ALG=HS256
```
