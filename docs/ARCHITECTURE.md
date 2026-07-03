# AI Travel Planner Assistant — Architecture

> System design, clean-architecture layering, data flow, and agent design. Complements [PLAN.md](./PLAN.md) (delivery) and [REQUIREMENTS.md](./REQUIREMENTS.md) (what/why).

## 1. System Context

```mermaid
flowchart TB
    User(["User (browser)"])

    subgraph app [Application]
        Web["Web (Next.js)"]
        API["API (FastAPI)"]
        Worker["Workers (Celery)"]
    end

    subgraph data [Data Stores]
        PG[("PostgreSQL + pgvector")]
        Redis[("Redis (queue/cache)")]
        Store[("S3 / MinIO (files)")]
    end

    subgraph external [External Services]
        Auth["Auth provider (Clerk)"]
        Flights["Flights API (Duffel)"]
        Hotels["Hotels API (Amadeus)"]
        LLM["LLM (OpenAI / Anthropic)"]
        Email["Gmail API (Phase 6)"]
    end

    User --> Web --> API
    API --> PG
    API --> Redis
    API --> Store
    API --> Auth
    API --> Flights
    API --> Hotels
    API --> LLM
    Worker --> PG
    Worker --> Store
    Worker --> LLM
    Redis --> Worker
    API -. Phase 6 .-> Email
```

**Responsibilities**
- **Web:** UI, auth session, SSE streaming of agent chat, approval modals.
- **API:** REST + SSE, request validation, orchestration, agent runtime.
- **Workers:** long-running jobs (PDF parsing, embedding, itinerary generation) off the request path.
- **Postgres + pgvector:** relational data plus document embeddings in one store.
- **Redis:** Celery broker + light caching.
- **S3/MinIO:** uploaded PDFs behind short-TTL signed URLs.

---

## 2. Clean Architecture (Backend)

Dependencies point inward. Business rules (`domain/`) never import frameworks or SDKs. External systems live behind interfaces in `adapters/`, so a mock and a real provider are interchangeable — this is what makes offline dev and CI possible without API keys.

```mermaid
flowchart TD
    subgraph outer [Frameworks and Drivers]
        FastAPI["FastAPI / SSE"]
        SDKs["Provider SDKs, SQLAlchemy, S3, LLM"]
    end
    subgraph interface [Interface Adapters]
        Routers["Routers + schemas"]
        Repos["Repositories"]
        ProviderImpl["Provider implementations"]
    end
    subgraph application [Application]
        Services["Services / use cases"]
    end
    subgraph enterprise [Enterprise / Domain]
        Domain["Entities, value objects, rules, guardrails"]
    end

    FastAPI --> Routers --> Services --> Domain
    SDKs --> Repos --> Services
    SDKs --> ProviderImpl --> Services
    ProviderImpl -.implements interface from.-> Domain
```

### Package structure (`apps/api/app/`)

| Path | Responsibility | May depend on |
|------|----------------|---------------|
| `domain/` | Entities (Trip, Itinerary, Budget), rules, guardrail predicates, provider interfaces | nothing external |
| `services/` | Use cases: search flights/hotels, parse doc, generate itinerary, draft email, calc budget | `domain/` |
| `adapters/providers/` | Duffel, Amadeus, and mock implementations of provider interfaces | `domain/` interfaces |
| `adapters/db/` | SQLAlchemy models, repositories, Alembic migrations | `domain/` |
| `adapters/storage/` | S3/MinIO client | — |
| `adapters/llm/` | LLM clients + versioned prompt registry | — |
| `agent/` | LangGraph graph, tools, guardrails, eval harness | `services/`, `domain/` |
| `api/` | Routers, request/response schemas, SSE | `services/` |
| `core/` | Config (Pydantic settings), logging, tracing, security, errors | — |

**Why this matters:** guardrails (no send/book without approval) live in `domain/` as pure, unit-testable predicates rather than as prompt text, so they cannot be bypassed by model output or prompt injection.

---

## 3. Data Flow: Plan a Trip (happy path)

```mermaid
sequenceDiagram
    actor U as User
    participant W as Web
    participant A as API (agent)
    participant P as Providers (mock/real)
    participant L as LLM
    participant DB as Postgres

    U->>W: "Plan my Tokyo trip"
    W->>A: POST /trips/:id/agent/chat (SSE)
    A->>A: intake -> clarify (if missing fields)
    A->>P: search_flights / search_hotels
    P-->>A: ranked results
    A->>DB: persist flights/hotels + agent_actions
    A->>L: generate_itinerary (structured output)
    L-->>A: validated itinerary JSON
    A->>DB: persist itinerary + items
    A->>A: calculate_budget vs trip.budget
    A-->>W: stream itinerary + tradeoffs + budget
    U->>W: Approve email draft
    W->>A: POST /emails/:id/approve
    A->>DB: mark approved + audit_log
```

Long jobs (PDF parse, embedding) are dispatched to Celery workers; the API streams status back over SSE. Correlation IDs propagate from the web request into worker jobs for end-to-end tracing.

---

## 4. Agent Design

### 4.1 State Machine (LangGraph)

```mermaid
stateDiagram-v2
    [*] --> intake
    intake --> clarify: missing required info
    clarify --> intake: user answers
    intake --> search: info complete
    search --> plan: results ready
    plan --> draftEmail: itinerary ready
    draftEmail --> awaitApproval: human-in-the-loop interrupt
    awaitApproval --> complete: user approves
    awaitApproval --> draftEmail: user edits/rejects
    complete --> [*]

    note right of awaitApproval
        Hard interrupt before send_email
        and book_hotel (book disabled in MVP)
    end note
```

### 4.2 Tools

| Tool | Layer it calls | Notes |
|------|----------------|-------|
| `search_flights` / `search_hotels` | services → providers | Mock by default; sandbox/real via config |
| `read_pdf` | services → db/pgvector | Returns chunks + source citation |
| `generate_itinerary` | services → llm | Structured output validated against schema |
| `calculate_budget` | domain | Pure function; no side effects |
| `draft_email` | services → llm | Produces draft only |
| `send_email` | services → email | Requires `user_approved == true` (guardrail) |
| `book_hotel` | — | Hard-disabled in MVP config |
| `get_weather` | services | Stub in MVP |

### 4.3 Guardrails (enforced in code)

- `send_email` and `book_hotel` are gated by `domain/` predicates that check explicit approval state, independent of LLM output.
- Tool outputs are validated against Pydantic schemas; invalid output → bounded repair retry → clear error.
- Every tool invocation is written to `agent_actions`; approvals to `audit_logs`.
- Uploaded document text is untrusted (see [REQUIREMENTS.md](./REQUIREMENTS.md#11-threat-model-lightweight-stride)).

---

## 5. Data Model

See [REQUIREMENTS.md §6](./REQUIREMENTS.md#6-data-model-core-tables) for the full table list. Key relationships:

```mermaid
erDiagram
    users ||--o{ trips : owns
    trips ||--|| trip_preferences : has
    trips ||--o{ flights : has
    trips ||--o{ hotels : has
    trips ||--o{ documents : has
    documents ||--o{ document_chunks : split_into
    trips ||--o{ itineraries : has
    itineraries ||--o{ itinerary_items : contains
    trips ||--o{ emails : has
    trips ||--o{ agent_actions : logs
    users ||--o{ audit_logs : generates
```

---

## 6. Cross-Cutting Concerns

| Concern | Approach | Reference |
|---------|----------|-----------|
| Config | Pydantic `BaseSettings`, validated at startup | [PLAN.md §6](./PLAN.md#6-environments--deployment) |
| Logging/Tracing | Structured JSON + OpenTelemetry, correlation IDs | [PLAN.md §7](./PLAN.md#7-observability--ops) |
| Errors | Central handler → user-friendly messages + Sentry | [ENGINEERING.md](./ENGINEERING.md) |
| Security | JWT auth, row-level authz, signed URLs, secret scanning | [REQUIREMENTS.md §5.1](./REQUIREMENTS.md#51-security-nfr-sec) |
| Retries | Exponential backoff on provider calls; graceful fallback | [REQUIREMENTS.md §5.3](./REQUIREMENTS.md#53-reliability-nfr-rel) |

---

## 7. Target Deployment (post-MVP)

MVP runs on `docker-compose`. The production target (documented, not built for MVP):

```mermaid
flowchart LR
    CDN["CDN / Web host"] --> WebProd["Web container"]
    WebProd --> APIProd["API containers (N)"]
    APIProd --> PGManaged[("Managed Postgres + pgvector")]
    APIProd --> RedisManaged[("Managed Redis")]
    APIProd --> ObjStore[("Object storage")]
    WorkerProd["Worker containers (N)"] --> PGManaged
    RedisManaged --> WorkerProd
```

- Container images tagged by SHA + SemVer; rollback via previous tag.
- Infrastructure as Code (Terraform) is the target for reproducible provisioning.
- Migrations run on deploy (expand/contract for backward compatibility).

---

## 8. Related Documents

- [PLAN.md](./PLAN.md) — Delivery plan and phase gates
- [REQUIREMENTS.md](./REQUIREMENTS.md) — Requirements, NFRs, threat model
- [ENGINEERING.md](./ENGINEERING.md) — Engineering practices
- [adr/](./adr/) — Architecture Decision Records
