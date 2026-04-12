# Guide

## Prerequisites

- Python 3.14+ with [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 22+ (see `.nvmrc`)
- pnpm 10.28+ (corepack enabled via root `package.json`)
- Docker (for PostgreSQL, Redis, MinIO)

**Evidence:** `server/pyproject.toml` (`requires-python = ">=3.14.0"`), `.nvmrc`, `package.json`, `DEVELOPMENT.md`

## Quick Start

### Option 1: dev CLI (recommended)

```bash
./dev/cli/install   # One-time: adds 'dev' alias
dev up              # Sets up everything: Docker, deps, migrations
```

**Evidence:** `DEVELOPMENT.md`, `dev/cli/`

### Option 2: Manual Setup

#### Environment Variables

```bash
./dev/setup-environment     # Creates server/.env and clients/apps/web/.env.local
```

For GitHub integration:
```bash
./dev/setup-environment --setup-github-app --backend-external-url https://yourdomain.ngrok.dev
```

For Stripe, add to `server/.env`:
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`

**Evidence:** `DEVELOPMENT.md`, `CLAUDE.md`

#### Start Infrastructure

```bash
cd dev/docker
docker compose -f docker-compose.dev.yml up -d   # PostgreSQL, Redis, MinIO
```

**Evidence:** `dev/docker/docker-compose.dev.yml`

#### Backend

```bash
cd server
uv sync                       # Install Python dependencies
uv run task db_migrate         # Run database migrations
uv run task api                # Start API server (http://127.0.0.1:8000)
uv run task worker             # Start Dramatiq worker (separate terminal)
```

**Evidence:** `server/pyproject.toml` (`[tool.taskipy.tasks]`), `AGENTS.md`

#### Frontend

```bash
cd clients
pnpm install                   # Install JS dependencies
pnpm dev                       # Start Next.js dev server (http://127.0.0.1:3000)
```

**Evidence:** `clients/package.json`, `AGENTS.md`

#### Emails

```bash
cd server
uv run task emails             # Build email templates
```

#### Backoffice

```bash
cd server
uv run task backoffice         # Build backoffice CSS/JS
```

**Evidence:** `server/pyproject.toml` (`[tool.taskipy.tasks]`)

## Common Tasks

### Run Tests

```bash
# Backend (all tests with coverage)
cd server && uv run task test

# Backend (fast, parallel, no coverage)
cd server && uv run task test_fast

# Backend (specific test)
cd server && uv run pytest tests/path/to/test_file.py::TestClass::test_method

# Frontend
cd clients && pnpm test

# Load tests
cd server && uv run task loadtest
```

**Evidence:** `server/pyproject.toml` (`[tool.taskipy.tasks]`), `AGENTS.md`

### Lint and Type Check

```bash
# Backend lint (auto-fix)
cd server && uv run task lint

# Backend lint (check only)
cd server && uv run task lint_check

# Backend type check
cd server && uv run task lint_types

# Frontend lint
cd clients && pnpm lint

# Frontend type check
cd clients && pnpm typecheck

# Frontend format
cd clients && pnpm format
```

**Evidence:** `server/pyproject.toml`, `clients/package.json`

### Database Migrations

```bash
cd server

# Apply pending migrations
uv run task db_migrate

# Generate migration from model changes
uv run alembic revision --autogenerate -m "description"

# Create empty migration (for data migrations)
uv run alembic revision -m "description"

# Recreate database (destructive)
uv run task db_recreate

# Fix conflicting migrations
uv run task db_reparent
```

**Evidence:** `server/pyproject.toml` (`[tool.taskipy.tasks]`), `AGENTS.md`

### Regenerate API Client

After backend API changes:

```bash
cd clients
pnpm run generate              # Regenerates TypeScript client from OpenAPI schema
```

**Evidence:** `AGENTS.md` (API Client Generation)

### Build for Production

```bash
# Frontend
cd clients && pnpm build

# Docker (API server)
cd server && docker build -t polar-api .
```

**Evidence:** `clients/package.json`, `server/Dockerfile`

## Deployment

- **Backend**: Deployed via Render (see `terraform/modules/render_service/`)
- **Frontend**: Deployment target not explicitly configured in repo (likely Vercel or similar)
- **Infrastructure**: Managed via Terraform (`terraform/`) with environments: production, sandbox, test
- **Pre-deploy hook**: `uv run task db_migrate` (runs Alembic upgrade)

**Evidence:** `terraform/`, `server/pyproject.toml` (`pre_deploy` task)

## Documentation

```bash
cd docs && pnpm dev            # Start Mintlify docs server locally
```

**Evidence:** `AGENTS.md`, `docs/`
