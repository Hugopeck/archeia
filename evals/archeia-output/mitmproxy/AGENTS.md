- This project uses uv. Always use `uv run pytest` and don't run pytest directly.
- To run all tests: `uv run tox`.
- When adding new source files, additionally run: `uv run tox -e individual_coverage -- FILENAME`.

---

# Archeia Agent Instructions

mitmproxy is a Python 3.12+ interactive intercepting proxy for HTTP/1, HTTP/2, WebSockets, TCP, UDP, and DNS. It ships three CLI entry points (`mitmproxy`, `mitmdump`, `mitmweb`) and a React/TypeScript web frontend. The core is a Python asyncio event loop (`mitmproxy/master.py`) driving a layered proxy pipeline (`mitmproxy/proxy/`) with a hook-based addon system (`mitmproxy/addonmanager.py`). A Rust extension (`mitmproxy_rs`) handles WireGuard and local redirect modes.

**Evidence:** `pyproject.toml`, `README.md`, `mitmproxy/master.py`

## Tech Stack

- **Language:** Python ≥3.12 (CPython only)
- **Package manager:** uv (`uv.lock`)
- **Key Python deps:** asyncio, tornado (web server), urwid (console UI), cryptography + pyOpenSSL (TLS), h2 (HTTP/2), aioquic (QUIC/HTTP3), mitmproxy_rs (Rust extension)
- **Frontend:** TypeScript + React + Vite (in `web/`)
- **Test framework:** pytest + pytest-asyncio + pytest-cov + tox
- **Linter:** ruff; **formatter:** ruff format; **type checker:** mypy

**Evidence:** `pyproject.toml`, `web/package.json`

## Setup

```bash
# Python environment (uv handles everything)
git clone https://github.com/mitmproxy/mitmproxy.git
cd mitmproxy
uv run mitmproxy --version

# Web frontend (only if modifying web/)
cd web && npm install
```

**Evidence:** `CONTRIBUTING.md`

## Dev Commands

```bash
uv run mitmproxy          # Interactive terminal UI
uv run mitmdump           # CLI flow recorder
uv run mitmweb            # Web UI
uv run tox -e lint        # Lint (ruff check .)
uv run tox -e fix         # Auto-fix lint + format
uv run tox -e mypy        # Type check
uv run tox                # Full test + lint + type check suite
uv run pytest test/mitmproxy/addons/test_anticache.py  # Targeted test
```

**Evidence:** `CONTRIBUTING.md`, `pyproject.toml`

## Testing Conventions

- Test files live in `test/mitmproxy/` and mirror source structure exactly
- Test file naming: `test_<module>.py`
- Use `@pytest.mark.asyncio` for async tests
- Coverage is enforced: `tox -e individual_coverage` checks per-module coverage
- The project targets 100% coverage for some modules — always add tests for new code
- Do not import from `test/` in source; the test package is separate

**Evidence:** `CONTRIBUTING.md`, `pyproject.toml`

## Project Structure and Module Boundaries

- `mitmproxy/` — core package; all public-facing code lives here
- `mitmproxy/proxy/` — asyncio server and protocol layer pipeline; do not bypass the layer abstraction
- `mitmproxy/addons/` — built-in addon implementations; new behaviors belong here as addons
- `mitmproxy/contrib/` — vendored third-party code; do not modify, lint, or type-check this directory
- `web/gen/` — generated TypeScript from the Python option schema; do not hand-edit
- `examples/` — addon examples; exempt from TID251 lint rule
- Entry points: `mitmproxy/tools/main.py` (console + dump + web), `mitmproxy/proxy/server.py` (proxy core)

**Evidence:** `mitmproxy/master.py`, `pyproject.toml`

## Coding Standards

**Formatting:** ruff format. Run `uv run tox -e fix` to apply. No manual formatting.

**Linting:** ruff with rules E, F, I, TID251. Key constraint: never use `asyncio.create_task` directly — use `mitmproxy.utils.asyncio_utils.create_task` to avoid garbage collection issues.

**Type checking:** mypy with `check_untyped_defs = true`. All new code in `mitmproxy/` must be type-annotated. `mitmproxy/py.typed` marks this as a typed package.

**Naming:** snake_case throughout Python source. TypeScript uses PascalCase for React components and camelCase for functions/variables.

**Imports:** ruff isort enforces single-line imports and section order (future → stdlib → third-party → local-folder → first-party). No wildcard imports.

**Logging:** `logging.getLogger(__name__)` per module. Do not use `print` in library code.

**Error handling and logging:** No structured logging framework. Follow the pattern in the nearest module. Use standard Python logging levels.

**Evidence:** `pyproject.toml`, `mitmproxy/master.py`

## Addon Development

Addons are Python classes with hook methods matching event names exactly (`def request(self, flow: HTTPFlow)`, `def response(self, flow)`, etc.). Register with `addonmanager.AddonManager`. Load at runtime with `-s addon.py`. See `examples/addons/` for patterns.

**Evidence:** `mitmproxy/addonmanager.py`, `mitmproxy/hooks.py`, `examples/README.md`

## Web Frontend (mitmweb)

- React + TypeScript + Vite; source in `web/src/`
- `web/gen/` is generated — regenerate with `cd web && npm run build`
- Tests use Jest (`web/package.json`)
- The web backend is `mitmproxy/tools/web/app.py` (Tornado); REST API + WebSocket at `/updates`
- Do not add new REST endpoints without a corresponding frontend integration

**Evidence:** `web/package.json`, `mitmproxy/tools/web/app.py`
