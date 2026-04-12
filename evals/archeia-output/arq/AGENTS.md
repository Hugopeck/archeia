# AGENTS.md

arq is a Python asyncio job queue library backed by Redis. It ships two runtime concerns: an `ArqRedis` client (for enqueuing jobs from application code) and a `Worker` process (long-running asyncio loop that polls Redis, executes coroutines, and writes results). There is no web framework, no ORM, and no database — all state is in Redis using key-prefix namespacing defined in `arq/constants.py`.

**Evidence:** `pyproject.toml`, `arq/connections.py`, `arq/worker.py`

## Tech Stack

- **Language:** Python 3.9–3.13
- **Async runtime:** asyncio (all worker execution is async)
- **Package manager:** uv (≥ 0.8.4); lockfile is `uv.lock`
- **Build backend:** hatchling
- **Key deps:** `redis[hiredis]>=4.2.0,<6`, `click>=8.0`; optional `watchfiles>=0.16`
- **Linter:** ruff (`[tool.ruff]` in `pyproject.toml`)
- **Formatter:** ruff format
- **Type checker:** mypy strict
- **Test runner:** pytest + pytest-asyncio (asyncio_mode = 'auto')

**Evidence:** `pyproject.toml`

## Setup

```bash
make install       # uv sync + pre-commit install
```

**Evidence:** `Makefile`

## Dev Commands

```bash
make test          # uv run coverage run -m pytest
make testcov       # test + open HTML coverage report
make lint          # uv run ruff check arq tests
make format        # uv run ruff check --fix + ruff format
make mypy          # uv run mypy arq
make all           # lint + mypy + testcov
make docs          # build Sphinx HTML docs
make clean         # remove caches, build artefacts
```

**Evidence:** `Makefile`

## Testing Conventions

- Tests live in `tests/`, named `test_*.py`.
- pytest-asyncio is configured with `asyncio_mode = 'auto'` — all `async def` test functions run automatically.
- Tests require Docker: testcontainers spins up a real Redis instance. No mocks for Redis.
- Fixture `arq_redis` provides a flushed `ArqRedis` instance; `worker` fixture provides a factory for `Worker` instances.
- Control Redis version via `ARQ_TEST_REDIS_VERSION` env var (default: `latest`).
- Test timeout is 10 seconds per test.

**Evidence:** `tests/conftest.py`, `pyproject.toml`

## Project Structure

```
arq/
  connections.py   — ArqRedis, RedisSettings, create_pool
  worker.py        — Worker class, Function wrapper, job execution loop
  jobs.py          — JobDef, JobResult, JobStatus enum, serialisation
  cron.py          — CronJob, next_cron scheduler
  cli.py           — Click CLI entrypoint
  constants.py     — Redis key prefixes (do not change without updating all consumers)
  utils.py         — time helpers, import_string, poll generator
  typing.py        — shared type aliases
tests/             — pytest test suite (one file per arq module)
docs/              — Sphinx documentation source
```

**Evidence:** `arq/worker.py`, `arq/connections.py`, `arq/jobs.py`, `arq/cron.py`, `arq/cli.py`

## Coding Standards

**Formatting:** ruff format configured (`[tool.ruff.format]`). Single quotes inline, double quotes multiline. Line length 120. Run `make format` before committing.

**Linting:** ruff with Q, RUF100, C90, UP, I rule sets. Run `make lint`. Max mccabe complexity: 13.

**Type checking:** mypy strict. All public API must be fully typed. `arq/typing.py` holds shared type aliases (`SecondsTimedelta`, `WorkerCoroutine`, `WorkerSettingsType`). Run `make mypy`.

**Naming:** snake_case for all file names, functions, and constants. PascalCase for classes. Constants live in `arq/constants.py` — add new constants there, not inline.

**Pre-commit:** hooks run format and mypy on every Python commit. Do not bypass with `--no-verify`.

**Evidence:** `pyproject.toml`, `.pre-commit-config.yaml`, `Makefile`

## Key Constraints

- **No sync code in worker coroutines.** The worker is a single asyncio event loop. Blocking calls will stall all concurrent jobs.
- **Serialisation is pluggable but defaults to pickle.** Custom `job_serializer`/`job_deserializer` can be passed to `ArqRedis`. If you add serialisation, ensure both sides (enqueue and worker) use the same serialiser.
- **Redis key prefixes in `constants.py` are load-bearing.** Changing a prefix breaks in-flight jobs. Coordinate any rename carefully.
- **`py.typed` marker at `arq/py.typed` declares this a PEP 561 typed package.** Do not remove it.
- **Sentinel mode** is available via `RedisSettings(sentinel=True)`. Tests do not cover this path — be cautious when modifying `connections.py` Sentinel logic.

**Evidence:** `arq/worker.py`, `arq/constants.py`, `arq/connections.py`, `arq/py.typed`

## Evidence

All facts above trace to: `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `arq/connections.py`, `arq/worker.py`, `arq/jobs.py`, `arq/cron.py`, `arq/cli.py`, `arq/constants.py`, `tests/conftest.py`, `.github/workflows/ci.yml`
