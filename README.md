# AI Travel Planner Assistant

An AI-powered travel planning assistant that searches flights and hotels, reads travel PDFs, generates itineraries, and drafts emails — with explicit user approval before anything is sent or booked.

![status](https://img.shields.io/badge/status-mvp-green)
![stage](https://img.shields.io/badge/stage-email%20%26%20polish-lightgrey)

## Status

**MVP complete** — trips, search, documents/RAG, agent itinerary, email drafts with approval, and activity audit feed.

## Quick start (no Docker)

Host-local mode uses **SQLite** + **local file storage**. No Postgres, Redis, MinIO, or Docker required.

### Prerequisites

- Python 3.11+
- Node.js 20+

### Start

```powershell
# From the repo root (Windows)
.\scripts\dev.ps1
```

Or in two terminals:

```powershell
# Terminal 1 — API
cd apps\api
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload

# Terminal 2 — Web
cd apps\web
npm install
npm run dev -- -H 0.0.0.0 -p 3000
```

> **Port note:** the API uses **8010** by default so it does not collide with other apps often bound to `8000`. The web app reads `NEXT_PUBLIC_API_URL` from `apps/web/.env.local`.

Open:

| Service | URL |
|---------|-----|
| Web | http://localhost:3000 |
| API health | http://localhost:8010/health |
| API ready | http://localhost:8010/ready |
| API docs | http://localhost:8010/docs |

Dev auth is on by default (`AUTH_DISABLED=true`) — no Clerk keys needed.

Data is stored under `apps/api/data/` (SQLite DB + uploaded PDFs).

## Optional: Docker Compose

If you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed:

```bash
cp .env.example .env
docker compose up --build
```

Compose overrides host-local defaults with Postgres, Redis, and MinIO.

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
apps/api          # FastAPI backend
packages/shared   # Shared TypeScript types
docs/             # Requirements, plan, architecture, ADRs, runbook
scripts/dev.ps1   # Host-local start script
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
- **Backend:** FastAPI + uvicorn (clean architecture), agent tools (Phase 4)
- **Database:** SQLite (host-local) or PostgreSQL + pgvector (Docker)
- **Storage:** Local filesystem (host-local) or S3 / MinIO (Docker)
- **CI/CD:** GitHub Actions

## Next steps

1. Run `.\scripts\dev.ps1` and open http://localhost:3000
2. Create a Tokyo trip → **Chat** → “Plan my trip” → review **Itinerary** → **Email** (approve → download `.eml`) → **Activity**
3. Post-MVP ideas — see [docs/PLAN.md](./docs/PLAN.md#13-post-mvp-roadmap)
