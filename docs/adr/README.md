# Architecture Decision Records

This directory records significant architecture and technology decisions using lightweight ADRs (see [ADR-0001](./0001-record-architecture-decisions.md)).

Each ADR captures the context, the decision, and its consequences at a point in time. ADRs are immutable once accepted; to change a decision, add a new ADR that supersedes the old one.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](./0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](./0002-backend-framework.md) | Backend framework: FastAPI | Accepted |
| [0003](./0003-auth-provider.md) | Auth provider: Clerk | Accepted |
| [0004](./0004-flight-api.md) | Flight API: Duffel + mock | Accepted |
| [0005](./0005-hotel-api.md) | Hotel API: Amadeus + mock | Accepted |
| [0006](./0006-repo-layout.md) | Repository layout: monorepo | Accepted |

## Format

```
# ADR-NNNN: Title

Status: Proposed | Accepted | Superseded by ADR-XXXX
Date: YYYY-MM-DD

## Context
## Decision
## Consequences
## Alternatives considered
```
