# Guide

## Prerequisites

- Python ≥3.12 (CPython; 3.12, 3.13, or 3.14 — from `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/) — the package manager; install separately
- Node.js ≥18 + npm — only needed to build or develop the web frontend (`web/`)
- No system services required (no database, no external services)

**Evidence:** `pyproject.toml`, `.python-version`, `CONTRIBUTING.md`

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mitmproxy/mitmproxy.git
   cd mitmproxy
   ```

2. Install dependencies and verify:
   ```bash
   uv run mitmproxy --version
   ```
   `uv run` automatically creates `.venv/` and installs all dependencies from `uv.lock`.

3. Activate the virtualenv (optional, for direct command access):
   ```bash
   # Linux / macOS
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

4. (Web frontend only) Install Node dependencies:
   ```bash
   cd web && npm install
   ```

**Evidence:** `CONTRIBUTING.md`, `pyproject.toml`, `web/package.json`

## Development Commands

### Run the proxy

```bash
uv run mitmproxy          # Interactive terminal UI
uv run mitmdump           # CLI flow recorder (stdout)
uv run mitmweb            # Web UI (browser at http://localhost:8081)
```

### Lint and format

```bash
uv run tox -e lint        # Check: ruff check .
uv run tox -e fix         # Fix: ruff check --fix-only . && ruff format .
```

### Type check

```bash
uv run tox -e mypy        # Run mypy on mitmproxy/, examples/addons/, release/*.py
```

### Web frontend

```bash
cd web
npm run dev               # Dev server with HMR (requires mitmweb running)
npm run build             # Production build to web/gen/
npm test                  # Run Jest tests
```

**Evidence:** `pyproject.toml`, `CONTRIBUTING.md`, `web/package.json`

## Testing

### Run full test suite

```bash
uv run tox                # Runs all tox environments (lint, mypy, py3.12/3.13/3.14)
uv run tox -e py          # Python tests only
```

### Run targeted tests

```bash
uv run pytest test/mitmproxy/addons/test_anticache.py \
  --cov mitmproxy.addons.anticache \
  --cov-report term-missing
```

### Run offline tests

```bash
uv run tox -e test-offline    # Uses test/run-tests-offline.sh
```

### Coverage

```bash
uv run tox -e individual_coverage    # Per-module coverage enforcement
```

**Evidence:** `CONTRIBUTING.md`, `pyproject.toml`

## Common Tasks

### Write an addon

Create a Python file implementing hook methods and load it with `-s`:

```bash
uv run mitmproxy -s examples/addons/log_events.py
```

See `examples/addons/` for reference addon patterns.

**Evidence:** `examples/README.md`, `mitmproxy/addonmanager.py`

### Save and replay flows

```bash
uv run mitmdump -w /tmp/flows.bin          # Capture flows to file
uv run mitmdump -r /tmp/flows.bin          # Replay captured flows
```

**Evidence:** `mitmproxy/io/`, `README.md`

### Build release artifacts

```bash
# Docker image
cd release/docker && docker build .

# Python package
uv run python -m build
```

**Evidence:** `release/docker/Dockerfile`, `release/README.md`, `pyproject.toml`

### Update web frontend build

```bash
cd web
npm run build              # Builds to web/gen/ -- committed to repo
```

**Evidence:** `web/package.json`, `web/README.md`
