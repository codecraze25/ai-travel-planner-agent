# ADR-0001: Record architecture decisions

Status: Accepted
Date: 2026-07-03

## Context

The project has several significant technology and design decisions (backend framework, auth, travel APIs, repo layout). Without a record, the rationale is lost and decisions get silently revisited. This is a portfolio-grade project intended to demonstrate real engineering practice.

## Decision

Use lightweight Architecture Decision Records (ADRs), one Markdown file per decision in `docs/adr/`, following Michael Nygard's format. ADRs are immutable once accepted; a change is a new ADR that supersedes the old one. Each ADR is reviewed via PR like any other change.

## Consequences

- Decisions are versioned, discoverable, and reviewable.
- New contributors (and reviewers) can understand why the system is the way it is.
- Small ongoing overhead to write an ADR for each significant decision.

## Alternatives considered

- **A wiki / Notion page:** drifts from the code and is not version-controlled with the repo.
- **Inline comments only:** too local; misses cross-cutting rationale.
