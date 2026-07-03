# AI Travel Planner Assistant — Runbook

> Operational guide: local setup, common operations, and failure recovery. Written to be usable during an incident. Note: implementation has not started yet, so commands below describe the intended workflow (Phase 0 will make them real).

## 1. Prerequisites

- Docker + Docker Compose
- Node.js 20+ and pnpm (web)
- Python 3.11+ and uv/pip (api)
- `make` (optional convenience targets)

## 2. Local Setup

```bash
# 1. Clone and copy env
cp .env.example .env
# fill in required values; defaults use mock providers (no API keys needed)

# 2. Start infrastructure + apps
docker compose up -d        # Postgres(+pgvector), Redis, MinIO, api, web

# 3. Run migrations + seed
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed_demo

# 4. Install pre-commit hooks (host)
pre-commit install
```

Verify:
- Web: http://localhost:3000
- API health: http://localhost:8000/health
- API readiness: http://localhost:8000/ready  (checks DB, Redis, storage)

By default `USE_MOCK_PROVIDERS=true`, so flight/hotel search works without external keys.

## 3. Common Operations

| Task | Command |
|------|---------|
| Tail API logs | `docker compose logs -f api` |
| Tail worker logs | `docker compose logs -f worker` |
| New migration | `docker compose exec api alembic revision --autogenerate -m "msg"` |
| Apply migrations | `docker compose exec api alembic upgrade head` |
| Rollback one migration | `docker compose exec api alembic downgrade -1` |
| Run backend tests | `docker compose exec api pytest` |
| Run web tests | `pnpm --filter web test` |
| Run agent eval | `docker compose exec api pytest tests/eval -q` |
| Rebuild after deps change | `docker compose build && docker compose up -d` |

## 4. Health & Readiness

- `/health` — process is alive. If failing: check container status (`docker compose ps`), restart the api service.
- `/ready` — dependencies reachable. If a dependency is red, see the matching runbook section below.

## 5. Failure Recovery

### 5.1 Database unavailable
- Symptom: `/ready` reports DB unhealthy; 500s on trip endpoints.
- Check: `docker compose ps postgres`, `docker compose logs postgres`.
- Fix: restart Postgres; verify `DATABASE_URL`; ensure migrations applied.

### 5.2 Redis / worker issues
- Symptom: PDF parse or itinerary jobs stuck in `pending`.
- Check: `docker compose logs -f worker`; Redis reachable; queue depth metric.
- Fix: restart worker; failed jobs persist their error payload (NFR-REL-03) and can be retried from the UI.

### 5.3 Storage (S3/MinIO) unavailable
- Symptom: upload URL generation fails; document uploads error.
- Check: MinIO console (http://localhost:9001), bucket exists, credentials valid.
- Fix: restart MinIO; recreate `travel-docs` bucket; verify signed-URL TTL config.

### 5.4 Flight/Hotel provider down
- Symptom: search returns errors or times out.
- Behavior: system retries with backoff (NFR-REL-01), then degrades to mock/cached data with a clear user message (NFR-REL-05).
- Fix: set `USE_MOCK_PROVIDERS=true` to continue working; check provider status page and API quota.

### 5.5 LLM provider errors / cost spike
- Symptom: agent chat fails or `api_usage` shows unusual cost.
- Check: LLM provider status; `api_usage` per-trip cost report; chat turn caps.
- Fix: switch `LLM_MODEL` to a cheaper model; verify structured-output retries are bounded; investigate any prompt-injection attempt in `agent_actions`.

### 5.6 Agent produced bad/unsafe output
- Guardrails are enforced in code: `send_email` requires approval; `book_hotel` is disabled. If an unapproved action is suspected, check `audit_logs` and the guardrail eval suite.
- Reproduce with the offending input as a new eval fixture; fix; add regression test.

## 6. Data Deletion (compliance)

To honor a deletion request (FR-DOC-05 / NFR-SEC-06):

```bash
docker compose exec api python -m app.scripts.delete_user_data --user <id>
```

This removes S3 objects, document rows, chunks, and associated trip data; the action is written to `audit_logs`.

## 7. Deploy & Rollback (target, post-MVP)

- Deploy: build image (tagged by SHA + SemVer) → push → run migrations → deploy → smoke test `/ready`.
- Rollback: redeploy previous image tag. Migrations are backward-compatible (expand/contract), so app rollback does not require a DB downgrade.

## 8. Related Documents

- [PLAN.md](./PLAN.md) — Delivery plan
- [ARCHITECTURE.md](./ARCHITECTURE.md) — System design
- [ENGINEERING.md](./ENGINEERING.md) — Engineering practices
