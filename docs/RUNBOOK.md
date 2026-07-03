# AI Travel Planner Assistant — Runbook

> Operational guide: host-local setup (default), optional Docker, and failure recovery.

## 1. Prerequisites

**Host-local (recommended when Docker is not installed):**
- Python 3.11+
- Node.js 20+

**Optional Docker stack:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

## 2. Host-local setup (no Docker)

Uses SQLite + local filesystem storage. No Postgres, Redis, or MinIO required.

```powershell
# From repo root
.\scripts\dev.ps1
```

Or two terminals:

```powershell
# Terminal 1 — API (port 8010 by default)
cd apps\api
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload

# Terminal 2 — Web
cd apps\web
npm install
npm run dev -- -H 0.0.0.0 -p 3000
```

| Check | URL |
|-------|-----|
| Web | http://localhost:3000 |
| API health | http://localhost:8010/health |
| API readiness | http://localhost:8010/ready |
| OpenAPI docs | http://localhost:8010/docs |

Defaults: `USE_MOCK_PROVIDERS=true`, `AUTH_DISABLED=true`, `STORAGE_BACKEND=local`.

Data lives under `apps/api/data/` (SQLite DB + uploads).

> **Port 8010:** chosen because another process often occupies `localhost:8000` on this machine. Configure via `API_PORT` and `apps/web/.env.local` (`NEXT_PUBLIC_API_URL`).

## 3. Docker Compose (optional)

```bash
cp .env.example .env
docker compose up --build
```

Compose overrides host-local defaults with Postgres, Redis, MinIO, and binds the API on **8000** inside Docker.

| Check | URL |
|-------|-----|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| MinIO console | http://localhost:9001 (`minioadmin` / `minioadmin`) |

## 4. Common Operations

| Task | Command |
|------|---------|
| Start host-local | `.\scripts\dev.ps1` |
| Start Docker stack | `docker compose up --build` |
| Stop Docker | `docker compose down` |
| Tail API (Docker) | `docker compose logs -f api` |
| Re-run migrations (Docker) | `docker compose exec api alembic upgrade head` |

## 5. Health & Readiness

- `/health` — process is alive (uvicorn is up).
- `/ready` — `database`, `redis`, `storage` reachable. In host-local mode Redis is optional and reports healthy when disabled.

## 6. Failure Recovery

### Port already in use
- Web (3000): stop the other Next.js process, or run `npm run dev -- -p 3001` and open that port.
- API (8010): set `API_PORT` and update `apps/web/.env.local` `NEXT_PUBLIC_API_URL`, then restart both.

### API health shows wrong app on :8000
- Another FastAPI app may be bound to `127.0.0.1:8000`. This project defaults to **8010** for host-local.

### Database errors (host-local)
- Delete `apps/api/data/travel.db` and restart the API (tables are recreated automatically).

### Docker not found
- Use host-local mode (`.\scripts\dev.ps1`) or install Docker Desktop.

## 7. Related Documents

- [PLAN.md](./PLAN.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [ENGINEERING.md](./ENGINEERING.md)
