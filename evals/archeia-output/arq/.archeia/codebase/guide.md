# Guide

> Development setup and common tasks for the arq codebase

## Prerequisites

- Python 3.9–3.13
- [uv](https://docs.astral.sh/uv/) (package manager) — version ≥ 0.8.4
- Docker (for running Redis via testcontainers in tests)

**Evidence:** `pyproject.toml`, `.github/workflows/ci.yml`, `tests/conftest.py`

## Setup

```bash
# Install all dependency groups and extras, then install pre-commit hooks
make install
```

This runs `uv sync --frozen --all-groups --all-packages --all-extras` and `uv run pre-commit install`.

**Evidence:** `Makefile`

## Running Tests

```bash
# Run full test suite with coverage
make test

# Run tests and open coverage HTML report
make testcov
```

Tests spin up a Redis container via testcontainers — Docker must be running. Control the Redis version with:

```bash
ARQ_TEST_REDIS_VERSION=7 make test
```

**Evidence:** `Makefile`, `tests/conftest.py`, `.github/workflows/ci.yml`

## Linting and Formatting

```bash
# Check linting and format (CI equivalent)
make lint

# Auto-fix lint issues and reformat
make format

# Type check
make mypy

# Run all (lint + mypy + testcov)
make all
```

**Evidence:** `Makefile`, `pyproject.toml`

## Building Docs

```bash
# Build Sphinx HTML docs
make docs
# Output: docs/_build/html/index.html
```

**Evidence:** `Makefile`, `.github/workflows/ci.yml`

## Running the Worker (Development)

```bash
# Start a worker (worker_settings is an importable Python class)
arq mymodule.WorkerSettings

# Burst mode (exit when queue is empty)
arq --burst mymodule.WorkerSettings

# Health check
arq --check mymodule.WorkerSettings

# Watch a directory and reload on file changes (requires watchfiles extra)
arq --watch ./src mymodule.WorkerSettings
```

**Evidence:** `arq/cli.py`

## Release Workflow

1. Update version in `arq/version.py`
2. Push a git tag — CI runs lint + docs + tests, then publishes to PyPI and Netlify automatically

**Evidence:** `.github/workflows/ci.yml`, `Makefile`

## Cleaning Build Artifacts

```bash
make clean
```

Removes `__pycache__`, `.coverage`, `.pytest_cache`, `.mypy_cache`, `htmlcov`, `*.egg-info`.

**Evidence:** `Makefile`
