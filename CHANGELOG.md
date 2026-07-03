# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project planning documentation set:
  - `docs/REQUIREMENTS.md` — functional/non-functional requirements, threat model, requirement traceability.
  - `docs/PLAN.md` — real-world delivery plan: ways of working, clean architecture, CI/CD, environments, observability, phase gates, AI engineering practices.
  - `docs/ARCHITECTURE.md` — system context, clean-architecture layering, data flow, agent state machine.
  - `docs/ENGINEERING.md` — engineering handbook (branching, commits, CI/CD, testing, security).
  - `docs/RUNBOOK.md` — local setup, operations, failure recovery.
  - `docs/adr/` — Architecture Decision Records (0001–0006).
  - `CONTRIBUTING.md` and this `CHANGELOG.md`.
- Phase 0 monorepo scaffold:
  - `apps/api` — FastAPI app with clean-architecture layout, `/health` + `/ready`, correlation IDs, Alembic bootstrap, tests.
  - `apps/web` — Next.js status page that calls the API health endpoints.
  - `packages/shared` — shared TypeScript domain types.
  - `docker-compose.yml` — Postgres (pgvector), Redis, MinIO, API, Web.
  - `.github/workflows/ci.yml` — lint, typecheck, test, build, security scans.
  - `.env.example`, pre-commit config, PR/issue templates.
- Phase 1 trip CRUD: users/trips migrations, trip API, dashboard, new trip form, trip detail shell, dev auth.
- Phase 2 travel search: mock flight/hotel providers, search/select endpoints, budget tracking, Flights/Hotels UI with tradeoff summaries and booking links.
- Phase 3 documents & RAG: PDF upload to S3/MinIO, PyMuPDF parsing, structured extraction, chunk embeddings, semantic search with source citations, Documents tab UI.
- Phase 4 agent & itinerary: mock agent chat (SSE), tool wiring (search, read_pdf, budget, generate_itinerary), guardrails, itinerary CRUD, Chat + Itinerary tabs, eval harness.
- Phase 5 email & polish: email drafts/templates, approve/reject, .eml export (no SMTP), activity audit feed, Privacy/Terms placeholders, host-local MVP demo path.
- Phase 6 send & calendar: mock email send provider (approval-gated), Gmail OAuth scaffold, calendar stub events on trip overview.

<!--
Template for future releases:

## [0.1.0] - YYYY-MM-DD
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->
