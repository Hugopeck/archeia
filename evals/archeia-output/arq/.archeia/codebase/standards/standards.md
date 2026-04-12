# Standards

> Python 3.9+ | uv | ruff (lint + format) | mypy strict | pytest + pytest-asyncio

## Language and Runtime

- **Language:** Python ≥ 3.9 (supports 3.9–3.13)
- **Package manager:** uv (`uv.lock` present; `[tool.uv]` in `pyproject.toml`)
- **Build backend:** hatchling (`pyproject.toml` `[build-system]`)

**Evidence:** `pyproject.toml`

## Formatting

- **Tool:** ruff format
- **Quote style:** single quotes for inline strings, double quotes for multiline (`[tool.ruff.format]`)
- **Line length:** 120 characters (`[tool.ruff]` `line-length = 120`)
- **Command:** `make format` → `uv run ruff format arq tests`
- Pre-commit hook runs `make format` on every Python file commit

**Evidence:** `pyproject.toml`, `.pre-commit-config.yaml`, `Makefile`

## Linting

- **Tool:** ruff
- **Target version:** py39
- **Active rule sets:** Q (quotes), RUF100 (unused noqa), C90 (complexity), UP (pyupgrade), I (isort)
- **Max complexity:** 13 (mccabe)
- **Command:** `make lint` → `uv run ruff check arq tests`

**Evidence:** `pyproject.toml`

## Type Checking

- **Tool:** mypy (strict mode — `strict = true`)
- **Command:** `make mypy` → `uv run mypy arq`
- Pre-commit hook runs mypy on every Python file commit
- `py.typed` marker present at `arq/py.typed` (PEP 561 typed package)

**Evidence:** `pyproject.toml`, `.pre-commit-config.yaml`, `arq/py.typed`

## Testing

- **Framework:** pytest with pytest-asyncio (`asyncio_mode = 'auto'`)
- **Test directory:** `tests/` (pattern: `test_*.py`)
- **Timeout:** 10 seconds per test (`timeout = 10` in `[tool.pytest.ini_options]`)
- **Redis:** tests use testcontainers (`testcontainers.redis.RedisContainer`) — no local Redis required; version controlled via `ARQ_TEST_REDIS_VERSION` env var
- **Coverage:** `coverage[toml]` with branch coverage; report via `make testcov`
- **Command:** `make test` → `uv run coverage run -m pytest`
- CI matrix: Python 3.9–3.13, Redis 5/6/7

**Evidence:** `pyproject.toml`, `tests/conftest.py`, `Makefile`, `.github/workflows/ci.yml`

## Naming Conventions

- **Files:** snake_case exclusively (`connections.py`, `worker.py`, `test_worker.py`)
- **Classes:** PascalCase (`ArqRedis`, `Worker`, `RedisSettings`, `JobDef`, `JobResult`)
- **Functions/methods:** snake_case (`create_pool`, `enqueue_job`, `run_worker`)
- **Constants:** snake_case, module-level in `arq/constants.py` (e.g., `default_queue_name`, `job_key_prefix`)
- **Private fixtures in tests:** prefixed with `_fix_` (e.g., `_fix_loop`) and aliased via `name=` parameter

**Evidence:** `arq/connections.py`, `arq/worker.py`, `arq/constants.py`, `tests/conftest.py`

## Pre-commit Hooks

The `.pre-commit-config.yaml` runs on every commit:
- `no-commit-to-branch` — prevents direct commits to `main`
- `check-yaml`, `check-toml` — syntax validation
- `end-of-file-fixer`, `trailing-whitespace` — whitespace hygiene
- `codespell` — spell checking
- `format` (local) — runs `make format`
- `mypy` (local) — runs `make mypy`

**Evidence:** `.pre-commit-config.yaml`

## CI/CD

Three jobs run on push to `main` and on pull requests: `lint`, `docs`, `test`. A `release` job publishes to PyPI and Netlify on version tag. All jobs must pass before release via the `check` (alls-green) gate.

**Evidence:** `.github/workflows/ci.yml`
