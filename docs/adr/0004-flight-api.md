# ADR-0004: Flight API — Duffel (sandbox) with mock provider

Status: Accepted
Date: 2026-07-03

## Context

Flight search (FR-FLIGHT-*) needs a provider with a developer-friendly API and a sandbox for building without production access. Real travel APIs are complex, and API approval can take time, so development and CI must not depend on live keys.

## Decision

Use **Duffel** as the flight provider for the MVP (sandbox environment), integrated behind a `FlightProvider` interface in `adapters/providers/`. Ship a **mock provider** with recorded fixtures as the default for local dev and CI (`USE_MOCK_PROVIDERS=true`).

## Consequences

- Clean developer UX and modern API; sandbox unblocks early work.
- Interface + mock means offline dev, deterministic tests, and easy provider swap.
- Duffel's coverage may differ from GDS-scale providers; acceptable for MVP planning use case.

## Alternatives considered

- **Amadeus for flights:** broader coverage but more complex API; chosen instead for hotels (ADR-0005).
- **Skyscanner/Kiwi:** partnership/approval friction for MVP.
