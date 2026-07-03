# AI Travel Planner Assistant

An AI-powered travel planning assistant that searches flights and hotels, reads travel PDFs, generates itineraries, and drafts emails — with explicit user approval before anything is sent or booked.

![status](https://img.shields.io/badge/status-phase%202-blue)
![stage](https://img.shields.io/badge/stage-travel%20search-lightgrey)

## Status

**Phase 2** — trip CRUD plus flight/hotel search (mock providers), tradeoff summaries, selection, and live budget bar. PDF/RAG is Phase 3.

## Quick start (Docker only)

You do **not** need a Python venv on your machine. The API container installs dependencies and runs **uvicorn** for you.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Start the stack

```bash
cp .env.example .env
docker compose up --build
```

On startup the `api` service:

1. Runs `alembic upgrade head` (creates `users` / `trips` tables)
2. Starts `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Open:

| Service | URL |
|---------|-----|
| Web | http://localhost:3000 |
| API health | http://localhost:8000/health |
| API ready | http://localhost:8000/ready |
| API docs | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 (`minioadmin` / `minioadmin`) |

Dev auth is on by default (`AUTH_DISABLED=true`) — no Clerk keys needed.

### Useful commands

```bash
docker compose up --build          # start everything
docker compose logs -f api         # watch uvicorn logs
docker compose down                # stop
docker compose exec api alembic upgrade head   # re-run migrations if needed
```

### Why no venv?

A **venv** is only for running Python tools *on the host* (outside Docker). With Docker:

- Dependencies install **inside** the `api` image
- **uvicorn** runs **inside** the container
- Postgres, Redis, and MinIO run as sibling containers

Host-side `apps/api/.venv` is optional and only useful if you want to run pytest/ruff without Docker.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md) | Functional/non-functional requirements, threat model, traceability |
| [docs/PLAN.md](./docs/PLAN.md) | Delivery plan: ways of working, CI/CD, phase gates, AI engineering |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System context, clean-architecture layers, agent design |
| [docs/ENGINEERING.md](./docs/ENGINEERING.md) | Engineering handbook |
| [docs/RUNBOOK.md](./docs/RUNBOOK.md) | Local setup, operations, failure recovery |
| [docs/adr/](./docs/adr/) | Architecture Decision Records |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution workflow |
| [CHANGELOG.md](./CHANGELOG.md) | Release history |

## Repository layout

```
apps/web          # Next.js frontend
apps/api          # FastAPI backend (uvicorn in Docker)
packages/shared   # Shared TypeScript types
docs/             # Requirements, plan, architecture, ADRs, runbook
.github/          # CI workflows and templates
docker-compose.yml
```

## MVP scope

- Trip creation with preferences
- Flight and hotel search (booking links only — no auto-book)
- PDF upload and structured extraction
- AI-generated day-by-day itinerary
- Email draft with manual approval
- LangGraph agent with guardrails and audit logging

## Tech stack

- **Frontend:** Next.js, React, TypeScript, Tailwind
- **Backend:** FastAPI + uvicorn (clean architecture), LangGraph (Phase 4)
- **Database:** PostgreSQL + pgvector
- **Queue:** Redis (+ Celery in Phase 3)
- **Storage:** S3 / MinIO
- **CI/CD:** GitHub Actions

## Next steps

1. Install Docker Desktop, then `docker compose up --build`
2. Create a Tokyo trip → Flights tab → Search → Select → Hotels tab → Search → Select
3. Phase 3 — PDF upload and RAG — see [docs/PLAN.md](./docs/PLAN.md#phase-3--documents--rag)
