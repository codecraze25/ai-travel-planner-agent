# AI Travel Planner Assistant

An AI-powered travel planning assistant that searches flights and hotels, reads travel PDFs, generates itineraries, and drafts emails — with explicit user approval before anything is sent or booked.

![status](https://img.shields.io/badge/status-planning-blue)
![stage](https://img.shields.io/badge/stage-MVP%20design-lightgrey)
<!-- CI/coverage badges added in Phase 0 once pipelines exist -->

## Status

**Planning phase** — requirements, delivery plan, architecture, and engineering practices are defined. Application code has not started; Phase 0 (project setup) is the next step.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md) | Functional/non-functional requirements, threat model, requirement traceability |
| [docs/PLAN.md](./docs/PLAN.md) | Delivery plan: ways of working, CI/CD, environments, phase gates, AI engineering |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System context, clean-architecture layers, data flow, agent design |
| [docs/ENGINEERING.md](./docs/ENGINEERING.md) | Engineering handbook: branching, commits, CI/CD, testing, security |
| [docs/RUNBOOK.md](./docs/RUNBOOK.md) | Local setup, operations, failure recovery |
| [docs/adr/](./docs/adr/) | Architecture Decision Records |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution workflow and self-review checklist |
| [CHANGELOG.md](./CHANGELOG.md) | Release history (SemVer + Keep a Changelog) |

## MVP Scope

- Trip creation with preferences
- Flight and hotel search (booking links only — no auto-book)
- PDF upload and structured extraction
- AI-generated day-by-day itinerary
- Email draft with manual approval
- LangGraph agent with guardrails and audit logging

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind
- **Backend:** FastAPI (clean architecture), LangGraph
- **Database:** PostgreSQL + pgvector
- **Queue:** Redis + Celery
- **Storage:** S3 / MinIO
- **CI/CD:** GitHub Actions (lint, typecheck, test, build, security, ai-eval)

Key technology choices are recorded as [ADRs](./docs/adr/).

## Engineering Principles

- Trunk-based development, Conventional Commits, PR-per-change with green CI
- Clean architecture with providers behind interfaces (mock + real)
- Guardrails enforced in code (no send/book without explicit approval)
- Observability from day one (structured logs, traces, metrics, audit)
- Enforceable phase gates: coverage, security, and observability

## Getting Started

Local setup and operations are documented in [docs/RUNBOOK.md](./docs/RUNBOOK.md#2-local-setup). These become runnable once Phase 0 lands.

## Next Steps

1. Confirm the recorded decisions in [docs/adr/](./docs/adr/).
2. Begin Phase 0 (project setup) from [docs/PLAN.md](./docs/PLAN.md#phase-0--project-setup).
3. Work the [First Sprint Backlog](./docs/PLAN.md#15-first-sprint-backlog-start-here).
