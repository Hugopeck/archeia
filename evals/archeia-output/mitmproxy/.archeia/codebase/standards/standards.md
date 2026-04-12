# Standards

## Documentation Confidence

| Section | Confidence | Reason |
|---------|------------|--------|
| Language and Runtime | high | Python ≥3.12, uv, from `pyproject.toml` and `.python-version` |
| Formatting and Linting | high | ruff configured in `pyproject.toml` with explicit rule selection |
| Typing and Static Analysis | high | mypy configured in `pyproject.toml` with `check_untyped_defs = true` |
| Project Structure | high | Clear `mitmproxy/` package, `test/`, `web/`, `examples/`, `release/` layout |
| Naming Conventions | high | All Python source files use snake_case; confirmed by file listing |
| Testing | high | pytest configured via `pyproject.toml`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |
| Error Handling and Logging | medium | Standard Python logging module used; pattern inferred from `mitmproxy/master.py` |

**Overall: medium** (1 medium, 6 high)

**Low-confidence guidance:**
- **Error Handling and Logging:** Use `logging.getLogger(__name__)` per module. Structured logging patterns are not enforced by config — follow the nearest module's pattern.

## Language and Runtime

- **Language:** Python ≥3.12 (CPython only; explicitly listed classifiers in `pyproject.toml`)
- **Runtime:** CPython 3.12, 3.13, 3.14 — tested across all three in CI
- **Package manager:** uv (`uv.lock` present; `uv run` is the standard invocation)
- **Frontend language:** TypeScript (strict mode), Node.js for build tooling

**Evidence:** `pyproject.toml`, `.python-version`, `uv.lock`, `web/tsconfig.json`

## Formatting and Linting

- **Linter:** ruff, configured in `pyproject.toml`
  - Rules selected: `E`, `F`, `I`, `TID251`
  - Ignored: `F541` (f-string without placeholders), `E501` (line length)
  - `TID251` bans `asyncio.create_task` — use `mitmproxy.utils.asyncio_utils.create_task` instead
  - `examples/` and `test/` are exempt from `TID251`
  - `mitmproxy/contrib/` is excluded from ruff entirely
- **Formatter:** ruff format (via `tox -e fix`)
- **Import order:** ruff isort with forced single-line imports, custom section order (future → stdlib → third-party → local-folder → first-party)
- **CI enforcement:** `tox -e lint` runs on every PR and blocks merge on failure

**Evidence:** `pyproject.toml`

## Typing and Static Analysis

- **Type checker:** mypy, configured in `pyproject.toml`
  - `check_untyped_defs = true`
  - `ignore_missing_imports = true`
  - Checks `mitmproxy/`, `examples/addons/`, `release/*.py`
  - Excludes `docs/`, `release/build/`, `examples/contrib/`, `test/`
  - `mitmproxy/contrib/` errors are ignored
- **Typed marker:** `mitmproxy/py.typed` present (PEP 561 typed package)
- **CI enforcement:** `tox -e mypy` runs on every PR

**Evidence:** `pyproject.toml`, `mitmproxy/py.typed`

## Project Structure

```
mitmproxy/          # Core Python package
  addons/           # Built-in addon implementations
  contentviews/     # Content rendering for different media types
  contrib/          # Vendored third-party code (not linted/typed)
  net/              # Low-level HTTP/DNS/TLS network primitives
  proxy/            # asyncio proxy server and protocol layer pipeline
  tools/            # Three UIs: console, dump, web
  utils/            # Shared utilities
web/                # React/TypeScript SPA (mitmweb frontend)
test/               # pytest test suite (mirrors mitmproxy/ structure)
examples/           # Addon examples (addons/) and community scripts (contrib/)
release/            # Docker, installer, and binary release artifacts
docs/               # Documentation source (MkDocs)
```

- `mitmproxy/contrib/` contains vendored code — do not modify or lint
- Test files mirror source structure: `test/mitmproxy/addons/test_anticache.py` tests `mitmproxy/addons/anticache.py`
- `web/gen/` contains generated TypeScript files — do not hand-edit

**Evidence:** `pyproject.toml`, `web/README.md`

## Naming Conventions

- **Python:** snake_case for all modules, functions, variables, and file names (consistent throughout `mitmproxy/`)
- **TypeScript/React:** PascalCase for React components, camelCase for variables and functions
- **Test files:** `test_<module>.py` prefix convention in `test/mitmproxy/`
- **Addon hooks:** method names match hook event names exactly (e.g., `def request(self, flow: HTTPFlow)`)

**Evidence:** `mitmproxy/addonmanager.py`, `test/mitmproxy/`

## Testing

- **Framework:** pytest with plugins: `pytest-asyncio`, `pytest-cov`, `pytest-timeout` (60s default), `pytest-xdist`
- **Test location:** `test/mitmproxy/` — mirrors source structure
- **Coverage target:** 100% enforced for some parts of the codebase; `pytest-cov` with XML output
- **Individual coverage check:** `tox -e individual_coverage` enforces per-module coverage
- **Async tests:** `pytest-asyncio` — use `@pytest.mark.asyncio` for async test functions
- **Run full suite:** `uv run tox` (uses tox matrix across Python versions)
- **Run targeted:** `uv run pytest test/mitmproxy/addons/test_anticache.py`

**Evidence:** `pyproject.toml`, `CONTRIBUTING.md`

## Error Handling and Logging

- **Logging:** standard `logging` module; `logging.getLogger(__name__)` per module
- **Log levels:** configured per logger in `mitmproxy/tools/main.py` (tornado → WARNING, asyncio → WARNING, hpack → WARNING)
- **asyncio exceptions:** unhandled asyncio task errors are caught in `Master._asyncio_exception_handler` and logged at ERROR level

**Evidence:** `mitmproxy/master.py`, `mitmproxy/tools/main.py`
