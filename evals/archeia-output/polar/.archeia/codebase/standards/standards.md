# Standards

## Language & Runtime

| Concern       | Backend                           | Frontend                         |
|---------------|-----------------------------------|----------------------------------|
| Language      | Python 3.14+                      | TypeScript                       |
| Runtime       | CPython / Uvicorn (ASGI)          | Node.js 22+ / Next.js            |
| Package mgr   | uv                                | pnpm 10.28+                      |
| Framework     | FastAPI                           | Next.js (React)                  |

**Evidence:** `server/pyproject.toml` (`requires-python = ">=3.14.0"`), `package.json` (`"packageManager": "pnpm@10.28.1"`), `.nvmrc`, `clients/pnpm-workspace.yaml`

## Formatting

- **Backend**: ruff format (configured in `server/pyproject.toml` `[tool.ruff]`, target `py312`)
  - Run: `uv run task lint` (auto-fixes with `ruff format . && ruff check --fix .`)
  - Check-only: `uv run task lint_check`
- **Frontend**: Prettier (configured in `clients/.prettierrc.json`)
  - Plugins: `prettier-plugin-organize-imports`, `prettier-plugin-tailwindcss`
  - Run: `pnpm format` (from clients/)

**Confidence: high**

**Evidence:** `server/pyproject.toml` (`[tool.ruff]`), `clients/.prettierrc.json`, `clients/package.json` (devDependencies)

## Linting

- **Backend**: ruff check with extended rules: `I` (isort), `UP` (pyupgrade), `T20` (print), `B039`, `PT` (pytest), `RUF022`, `RUF023`, `RUF10`, `RUF20`
  - Ignores: `F841` (unused vars), `PT012`
  - Per-file: migrations ignore `F401`, scripts ignore `T20`
- **Frontend**: ESLint (`eslint.config.js` in `clients/apps/app/`, `eslint.config.mjs` in `clients/apps/web/`)

**Confidence: high**

**Evidence:** `server/pyproject.toml` (`[tool.ruff.lint]`), `clients/apps/app/eslint.config.js`, `clients/apps/web/eslint.config.mjs`

## Type Checking

- **Backend**: mypy with strict settings (configured in `server/pyproject.toml` `[tool.mypy]`)
  - Pydantic plugin enabled
  - `disallow_untyped_defs = true`, `check_untyped_defs = true`, `strict_equality = true`
  - Run: `uv run task lint_types`
- **Frontend**: pyright for root (`pyrightconfig.json`); TypeScript strict mode via tsconfig

**Confidence: high**

**Evidence:** `server/pyproject.toml` (`[tool.mypy]`, `[tool.pydantic-mypy]`), `pyrightconfig.json`

## Testing

- **Backend**: pytest with asyncio strict mode
  - Location: `server/tests/` mirroring `server/polar/` structure
  - Config: `[tool.pytest.ini_options]` in `server/pyproject.toml`
  - Run: `uv run task test` (with coverage) or `uv run task test_fast` (parallel, no coverage)
  - Markers: `auth`
  - Fixtures: `SaveFixture`, `AsyncSession`, class-based tests, one class per method
  - Coverage: `[tool.coverage.run]` with greenlet concurrency
- **Frontend**: vitest (configured in `clients/apps/web/vitest.config.ts`, `clients/packages/checkout/vitest.config.ts`, `clients/packages/i18n/vitest.config.ts`)
  - Run: `pnpm test` (from clients/)

**Confidence: high**

**Evidence:** `server/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.coverage.*]`), `clients/apps/web/vitest.config.ts`

## Naming Conventions

| Context           | Convention  | Example                          |
|-------------------|-------------|----------------------------------|
| Python files      | snake_case  | `account_credit.py`              |
| Python classes    | PascalCase  | `Product`, `OrderService`        |
| TypeScript files  | camelCase   | `customerPortal.ts`              |
| React components  | PascalCase  | `CurrencySelector.tsx`           |
| UI components     | kebab-case  | `alert-dialog.tsx`               |
| API modules       | snake_case  | `checkout_link/`, `custom_field/`|

**Confidence: high** (Python consistently snake_case; TS mixed camelCase/PascalCase following React conventions)

**Evidence:** `server/polar/`, `clients/apps/web/src/`, `clients/packages/ui/src/components/`

## Backend Module Structure

Every domain module in `server/polar/` follows this pattern:

| File            | Role                          |
|-----------------|-------------------------------|
| `endpoints.py`  | FastAPI route definitions      |
| `service.py`    | Business logic (service class) |
| `repository.py` | SQLAlchemy queries             |
| `schemas.py`    | Pydantic request/response      |
| `tasks.py`      | Dramatiq background jobs       |
| `auth.py`       | Module-specific authenticators |

**Evidence:** `AGENTS.md` (Backend Conventions section)

## Database Conventions

- ORM: SQLAlchemy (async) with asyncpg driver
- Migrations: Alembic (`server/migrations/`)
- Models centralized in `server/polar/models/` (exception to module structure)
- Never call `session.commit()` in business logic; API middleware commits at request end, workers commit at task end
- Use `session.flush()` when needed for constraints/defaults
- Repository classes inherit from `RepositoryBase`
- Methods accept domain objects over UUIDs when available
- `flush: bool = False` as keyword-only parameter

**Evidence:** `AGENTS.md` (SQLAlchemy & Database Standards, Repository Layer Standards)

## Low-confidence Guidance

- **Frontend testing conventions**: Limited evidence for frontend test patterns beyond vitest config presence. Match existing test files.
- **Frontend state management**: Zustand mentioned in `AGENTS.md` but no config file found. Follow patterns in existing store files.
- **Pre-commit hooks**: Not configured. No automated pre-commit enforcement detected.
