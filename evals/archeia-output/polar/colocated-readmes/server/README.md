# server

Python backend for Polar's payment infrastructure platform. Exposes a REST API via FastAPI, processes background jobs via Dramatiq workers, and manages all business logic for products, subscriptions, checkouts, orders, benefits, and financial transactions.

## Structure

```mermaid
graph LR
    APP[app.py] -->|mounts| API[api.py routes]
    APP -->|mounts| BO[backoffice/]
    API -->|delegates| MOD[polar/{module}/endpoints.py]
    MOD -->|calls| SVC[{module}/service.py]
    SVC -->|queries| REPO[{module}/repository.py]
    REPO -->|reads/writes| DB[(PostgreSQL)]
    SVC -->|enqueues| WRK[worker/ Dramatiq]
    WRK -->|consumes| REDIS[(Redis)]
    APP -->|stores files| S3[(S3/MinIO)]
```

## Key Concepts

- **Module pattern** -- Each domain (checkout, order, subscription, benefit, etc.) lives in `polar/{module}/` with `endpoints.py`, `service.py`, `repository.py`, `schemas.py`, `tasks.py`, and `auth.py`. Models are the exception: centralized in `polar/models/`.
- **Dramatiq workers** -- Background jobs (webhook delivery, benefit grants, payment callbacks) are dispatched via `worker/` using Redis as the message broker. Worker entry point is `worker/run.py`.
- **Auth system** -- `AuthSubject[T]` where T is User, Organization, Customer, or Anonymous. Module-specific authenticators define required scopes and allowed subjects.
- **Session management** -- Never `session.commit()` in business logic. API middleware auto-commits; workers commit at task end. Use `session.flush()` for constraints.
- **Emails** -- Transactional email templates live in `emails/` and are compiled by a Node.js renderer (see `Dockerfile` build stage).

## Usage

The API server is consumed by the Next.js web dashboard (`clients/apps/web/`) via auto-generated TypeScript client (`clients/packages/client/`). External integrations use the REST API directly or via official SDKs.

## Learnings

_No learnings recorded yet. Add entries here as non-obvious discoveries are made during development._
