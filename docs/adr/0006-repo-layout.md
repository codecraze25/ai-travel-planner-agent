# ADR-0006: Repository layout — monorepo

Status: Accepted
Date: 2026-07-03

## Context

The project has a Next.js frontend, a FastAPI backend, and shared data contracts. We want type-safe boundaries between web and api, atomic changes across both, and a single CI pipeline, while remaining manageable for a solo developer.

## Decision

Use a **monorepo** with:

```
apps/web        # Next.js frontend
apps/api        # FastAPI backend (clean architecture)
packages/shared # Shared types / validation schemas
docs/           # Requirements, plan, architecture, ADRs, runbook
infra/docker/   # Compose + Dockerfiles
.github/        # CI workflows, templates
```

## Consequences

- Cross-cutting changes (e.g., a new field on Trip) land in one atomic PR across web + api + shared.
- Single CI pipeline and shared tooling config.
- Shared contracts reduce web/api drift (mitigates the two-language cost from ADR-0002).
- Slightly more complex tooling setup than two separate repos; acceptable and standard.

## Alternatives considered

- **Two separate repos (web, api):** simpler per-repo tooling, but coordinating cross-repo changes and versioning contracts is painful.
- **Single mixed app:** couples frontend and backend deploy lifecycles; rejected.
