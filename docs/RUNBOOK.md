# AI Travel Planner Assistant — Runbook

> Operational guide: Docker-first local setup, common operations, and failure recovery.

## 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

You do **not** need a host Python venv or Node install for day-to-day work. The `api` container runs **uvicorn**; the `web` container serves Next.js.

## 2. Local Setup (Docker)

```bash
cp .env.example .env
docker compose up --build
```

What happens on `api` start (`scripts/entrypoint.py`):

1. `alembic upgrade head` — applies migrations
2. `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Verify:

| Check | URL |
|-------|-----|
| Web | http://localhost:3000 |
| API health | http://localhost:8000/health |
| API readiness | http://localhost:8000/ready |
| OpenAPI docs | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 (`minioadmin` / `minioadmin`) |

Defaults: `USE_MOCK_PROVIDERS=true`, `AUTH_DISABLED=true` (no external keys).

### Why no venv?

| Approach | When to use |
|----------|-------------|
| **Docker (default)** | Normal development. Deps + uvicorn live in the container. |
| **Host venv** | Optional: run `pytest` / `ruff` on the host without Docker. Not required. |

## 3. Common Operations

| Task | Command |
|------|---------|
| Start stack | `docker compose up --build` |
| Stop stack | `docker compose down` |
| Tail uvicorn logs | `docker compose logs -f api` |
| Rebuild API only | `docker compose up --build api` |
| Re-run migrations | `docker compose exec api alembic upgrade head` |
| Rollback one migration | `docker compose exec api alembic downgrade -1` |
| Shell into API | `docker compose exec api sh` |

Source under `apps/api/app` is volume-mounted, so uvicorn `--reload` picks up code changes without rebuilding (unless you change `pyproject.toml` dependencies).

## 4. Health & Readiness

- `/health` — process is alive (uvicorn is up).
- `/ready` — `database`, `redis`, `storage` reachable. All should be `true` under Docker Compose.

## 5. Failure Recovery

### Docker not found
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), start it, and open a **new** terminal so `docker` is on PATH.

### Database unavailable
- Check: `docker compose ps postgres`, `docker compose logs postgres`
- Fix: `docker compose restart postgres`, then `docker compose restart api`

### Storage (MinIO) unavailable
- Check MinIO console http://localhost:9001
- Fix: `docker compose restart minio` (API creates the `travel-docs` bucket on startup)

### Migration failed on startup
- Check: `docker compose logs api`
- Fix: ensure Postgres is healthy, then `docker compose up --build api`

## 6. Optional: host-side tools (venv)

Only if you want to run tests without Docker:

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

This does **not** replace Docker for running the app.

## 7. Related Documents

- [PLAN.md](./PLAN.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [ENGINEERING.md](./ENGINEERING.md)
