# ADR-0002: Backend framework — FastAPI

Status: Accepted
Date: 2026-07-03

## Context

The backend hosts the REST/SSE API and, critically, the AI agent runtime (LangGraph) plus PDF/RAG processing. The AI and data-science ecosystem (LangGraph, LangChain, PyMuPDF, Unstructured, pgvector clients, OpenAI/Anthropic SDKs) is strongest in Python. We also need async I/O for streaming agent responses and concurrent provider calls.

## Decision

Use **FastAPI (Python 3.11+)** for the backend, structured with clean architecture (see [ARCHITECTURE.md](../ARCHITECTURE.md)). Use SQLAlchemy + Alembic for persistence/migrations, Celery + Redis for background jobs, and Pydantic for validation and typed settings.

## Consequences

- First-class access to the Python AI ecosystem and LangGraph.
- Native async support for SSE streaming and concurrent provider calls.
- Automatic OpenAPI docs from Pydantic schemas.
- Frontend and backend use different languages (TypeScript vs Python); shared contracts live in `packages/shared` to mitigate drift.

## Alternatives considered

- **NestJS (TypeScript):** single language across stack, but weaker AI/PDF ecosystem; LangGraph is Python-first. Rejected for MVP.
- **Django:** heavier and more opinionated than needed; async story less clean than FastAPI.
