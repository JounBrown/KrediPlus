# KrediPlus

Sistema de gestión de créditos con chatbot RAG integrado.

## Estructura del Proyecto

```
KrediPlus/
├── backend/          # API REST (Python/FastAPI)
├── frontend/         # SPA (React/TypeScript)
└── README.md
```

## Tech Stack

### Backend
- **Python 3.12** + **FastAPI**
- **PostgreSQL** (Supabase)
- **SQLAlchemy** (async)
- **OpenAI** (embeddings y chat)
- **Poetry** (gestión de dependencias)

### Frontend
- **React 19** + **TypeScript**
- **Vite**
- **TailwindCSS** + **shadcn/ui**
- **TanStack Router** + **React Query**
- **Zustand** (estado global)
- **Supabase Auth**

## Arquitectura Backend (Hexagonal)

```
backend/src/
├── domain/                    # Núcleo del negocio
│   ├── entities/              # Entidades de dominio
│   └── ports/                 # Interfaces (contratos)
│
├── application/               # Casos de uso
│   ├── services/              # Lógica de aplicación
│   └── dtos/                  # Data Transfer Objects
│
└── infrastructure/            # Adaptadores externos
    ├── inbound/               # Entrada (HTTP)
    │   └── api/
    │       ├── routes/
    │       └── middleware/
    │
    └── outbound/              # Salida (DB, Storage, APIs)
        ├── database/
        ├── openai_adapter.py
        ├── supabase_auth_adapter.py
        └── supabase_storage_service.py
```

## Requisitos

- Python 3.12+
- Node.js 18+
- pnpm
- Poetry
- Cuenta de Supabase
- API Key de OpenAI

## Instalación

### Backend

```bash
cd backend
poetry install
cp .env.example .env  # Configurar variables
poetry run uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
cp .env.example .env.local  # Configurar variables
pnpm run dev
```

## Variables de Entorno

### Backend (.env)
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
OPENAI_API_KEY=
DATABASE_URL=
```

### Frontend (.env.local)
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=
```

## Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /api/v1/clients | Crear cliente |
| GET | /api/v1/clients | Listar clientes |
| POST | /api/v1/credits | Crear crédito |
| POST | /api/v1/chat | Chat RAG |
| POST | /api/v1/rag/documents | Subir documento RAG |

## Tests

```bash
cd backend
poetry run pytest
poetry run pytest --cov=src  # Con coverage
```
