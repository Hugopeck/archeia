# Development Instructions for LLM agents

Polar is an open-source payment infrastructure platform for developers. It acts as a merchant of record handling billing, subscriptions, digital product sales, tax compliance, and customer management. The monorepo contains a Python/FastAPI backend, a Next.js web dashboard, shared TypeScript packages, Terraform infrastructure, and Mintlify documentation.

## Tech Stack

| Layer       | Technology                                               |
|-------------|----------------------------------------------------------|
| Backend     | Python 3.14+ / FastAPI / Uvicorn / SQLAlchemy / Dramatiq |
| Frontend    | TypeScript / Next.js / React / Tailwind CSS / Radix UI   |
| Database    | PostgreSQL (asyncpg) / Redis                             |
| Package mgr | uv (backend), pnpm 10.28 (frontend)                    |
| Infra       | Terraform / Docker / Render                              |
| Observability | Sentry / Logfire / Prometheus / PostHog                |

**Evidence:** `server/pyproject.toml`, `clients/package.json`, `package.json`

## Setup & Dev Commands

```bash
# Quick start
./dev/cli/install && dev up

# Or manual:
./dev/setup-environment                     # Generate .env files

# Backend (from server/)
uv sync && uv run task api                  # API at :8000
uv run task worker                          # Dramatiq worker

# Frontend (from clients/)
pnpm install && pnpm dev                    # Dashboard at :3000
```

**Evidence:** `DEVELOPMENT.md`, `server/pyproject.toml`

## Testing

```bash
# Backend
cd server
uv run task test                            # All tests + coverage
uv run task test_fast                       # Parallel, no coverage
uv run pytest tests/path/test_file.py       # Single file

# Frontend
cd clients && pnpm test
```

- Backend: pytest, asyncio strict mode, class-based tests (one class per method), test files mirror `server/polar/` structure under `server/tests/`
- Fixtures: `SaveFixture`, `AsyncSession`; avoid redundant fixture setup
- E2E tests (`test_task`, `test_endpoints`) do not use mocking

**Evidence:** `server/pyproject.toml`, `DEVELOPMENT.md`

## Linting & Type Checking

```bash
# Backend
cd server
uv run task lint                            # ruff format + ruff check --fix
uv run task lint_check                      # Check only
uv run task lint_types                      # mypy

# Frontend
cd clients
pnpm lint && pnpm typecheck && pnpm format  # ESLint, tsc, Prettier
```

**Evidence:** `server/pyproject.toml`, `clients/package.json`

## Project Structure

```
server/polar/           # Backend domain modules
  {module}/
    endpoints.py        # FastAPI routes
    service.py          # Business logic
    repository.py       # SQLAlchemy queries
    schemas.py          # Pydantic request/response
    tasks.py            # Dramatiq background jobs
    auth.py             # Module authenticators
  models/               # All SQLAlchemy models (centralized)
  kit/                  # Shared utilities

clients/                # Turborepo + pnpm workspace
  apps/web/             # Next.js merchant dashboard
  apps/app/             # Secondary Next.js app
  packages/ui/          # Shared React components (Radix UI + Tailwind)
  packages/client/      # Auto-generated TS API client
  packages/checkout/    # Embeddable checkout components
```

**Evidence:** `server/polar/`, `clients/pnpm-workspace.yaml`

## Coding Standards

**General:**
- No unnecessary comments; code should be self-explanatory
- Meaningful variable and function names
- SOLID principles; do not modify unrelated code

**Formatting:** ruff format (backend), Prettier (frontend). Run `uv run task lint` and `pnpm format`.

**Linting:** ruff (backend) with rules I, UP, T20, PT, RUF. ESLint (frontend apps).

**Type checking:** mypy strict (backend), pyright + TypeScript (frontend). Always prefix Python commands with `uv run`.

**Naming:** Python uses snake_case for files/functions, PascalCase for classes. TypeScript uses camelCase for files, PascalCase for React components.

**Evidence:** `server/pyproject.toml`, `clients/.prettierrc.json`

## Backend Patterns

- **Repository layer**: Accept domain objects over UUIDs when available. Return updated objects. Use `flush: bool = False` as keyword-only param. Inherit from `RepositoryBase`.
- **Service layer**: Proper exception handling with HTTP status codes (409 conflict, 422 validation, 404 not found). Include entity IDs in error messages. Use async/await with SQLAlchemy sessions.
- **Database**: Never call `session.commit()` in business logic — API middleware commits at request end, workers at task end. Use `session.flush()` for constraints/defaults.
- **Migrations**: `uv run alembic revision --autogenerate -m "description"`. After API changes, regenerate TS client: `cd clients && pnpm run generate`.
- **Authentication**: `AuthSubject[T]` with T in {User, Organization, Customer, Anonymous}. Module-specific `Authenticator` with scopes. Credential resolution: customer session → user cookie → OAuth2 → PAT → OAT → anonymous.
- **Imports**: Top of file, not inside methods. Import models from `polar.models`, services from modules.

**Evidence:** `DEVELOPMENT.md`, `server/polar/app.py`, `server/polar/auth/`

## Frontend Patterns

- **Data fetching**: TanStack Query with hooks from `@polar-sh/sdk`
- **State management**: Zustand for global state
- **UI components**: Use `clients/packages/ui` components (Radix UI + Tailwind CSS)
- **Styling**: Tailwind CSS only

**Evidence:** `clients/apps/web/`, `clients/packages/ui/`

## Key Integrations

- **Stripe**: Payment processing, subscriptions, payouts. Keys in `server/.env`.
- **GitHub**: OAuth authentication, repository benefit grants. Requires GitHub App.
- **S3/MinIO**: File uploads, invoices, downloadable content.
- **Redis**: Cache + Dramatiq job queue broker.
- **PostgreSQL**: Primary database, managed via Alembic migrations.

**Evidence:** `server/pyproject.toml`, `DEVELOPMENT.md`, `dev/docker/docker-compose.dev.yml`
