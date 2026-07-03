# Contributing

This project follows a professional workflow even though it is (currently) solo-developed. It keeps history clean, changes reviewable, and `main` always releasable. See [docs/ENGINEERING.md](./docs/ENGINEERING.md) for the full handbook.

## Workflow

1. **Branch** from `main`: `feat/…`, `fix/…`, `chore/…`, `docs/…`, `refactor/…`.
2. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`.
3. **Keep PRs small** and focused on one requirement.
4. **Open a PR** — CI must be green (lint, typecheck, test, build, security, ai-eval).
5. **Self-review** using the checklist below.
6. **Squash-merge** and delete the branch.

Direct pushes to `main` are disabled (branch protection).

## Commit types

`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`

Example: `feat(flights): add Duffel provider adapter`

## Self-review checklist

- [ ] Requirement ID referenced (`FR-*` / `NFR-*`)
- [ ] Tests added/updated; coverage gate green (domain/services ≥ 80%, backend ≥ 70%)
- [ ] Lint, typecheck, and security scans pass
- [ ] Observability added where relevant (logs/traces/metrics)
- [ ] Docs updated (README / RUNBOOK / ADR)
- [ ] Traceability row updated in [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md#12-requirement-traceability)
- [ ] CHANGELOG entry added
- [ ] No secrets, debug prints, or commented-out code

## Local setup

See [docs/RUNBOOK.md](./docs/RUNBOOK.md#2-local-setup). Install pre-commit hooks so local checks mirror CI:

```bash
pre-commit install
```

## Decisions

Significant technology or design changes require an ADR in [docs/adr/](./docs/adr/). Add a new ADR rather than editing an accepted one.

## Definition of Done

A change is done only when it meets the Definition of Done in [docs/PLAN.md](./docs/PLAN.md#24-definition-of-done-dod).
