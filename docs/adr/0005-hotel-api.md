# ADR-0005: Hotel API — Amadeus (sandbox) with mock fallback

Status: Accepted
Date: 2026-07-03

## Context

Hotel search (FR-HOTEL-*) needs a provider with hotel content and a sandbox. Full booking-partner APIs (e.g., Booking.com) require partnership approval that is out of scope for an MVP that only shows booking links (no auto-book).

## Decision

Use **Amadeus** (self-service sandbox) as the hotel provider, behind a `HotelProvider` interface, with a **mock provider** as the default fallback for local dev and CI. MVP shows booking links only; no booking is performed.

## Consequences

- Sandbox access without a partnership; enough content for planning + links.
- Interface + mock keeps dev offline-capable and tests deterministic.
- Amadeus hotel content/quality may be limited in sandbox; acceptable since MVP does not book.
- Real booking (Phase 8) will require a partner API and a new ADR.

## Alternatives considered

- **Booking.com / Expedia partner APIs:** require approval; deferred to booking phase.
- **Mock-only for MVP:** simplest, but we want at least one real sandbox integration to prove the adapter design.
