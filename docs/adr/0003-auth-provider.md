# ADR-0003: Auth provider — Clerk (NextAuth fallback)

Status: Accepted
Date: 2026-07-03

## Context

The MVP needs sign-up, login, and session management quickly, without building password storage, reset flows, and OAuth from scratch. Security requirements (NFR-SEC-01/04) demand robust auth and per-user authorization. The frontend is Next.js.

## Decision

Use **Clerk** as the primary auth provider for the MVP: hosted UI components, session management, and JWTs the FastAPI backend validates. Keep **NextAuth** as a documented fallback if we need fully self-hosted auth or want to avoid a third-party dependency.

## Consequences

- Fast, secure auth with minimal custom code; good Next.js integration.
- Backend validates Clerk-issued JWTs and enforces row-level ownership.
- External dependency and potential cost at scale; mitigated by keeping the auth boundary thin so swapping providers is feasible.

## Alternatives considered

- **NextAuth:** self-hosted, flexible, free; more wiring for the same result. Retained as fallback.
- **Auth0:** capable but heavier setup than needed for MVP.
- **Roll your own:** highest risk and effort; rejected.
