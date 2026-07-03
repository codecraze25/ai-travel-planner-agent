# API (`apps/api`)

FastAPI backend for the AI Travel Planner Assistant.

## Layout

```
app/
├── api/            # routers, middleware
├── services/       # use cases (Phase 1+)
├── domain/         # entities and rules (Phase 1+)
├── adapters/       # db, storage, providers, llm
├── agent/          # LangGraph agent (Phase 4)
├── core/           # config, logging
└── main.py
```

## Local (without Docker)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest
```
