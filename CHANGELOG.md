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
