# Architecture

## Documentation Confidence

| Section | Confidence | Reason |
|---------|------------|--------|
| System Overview | high | Manifest description, README, and entry points clearly identified from `pyproject.toml` and `README.md` |
| Topology | high | Directory structure, multiple entry points, and Dockerfile present in `release/docker/` |
| Module Boundaries | high | Clear package structure under `mitmproxy/` with distinct subdirectories |
| Data Flow | medium | Primary flow inferred from `mitmproxy/proxy/server.py`, `mitmproxy/master.py`, and `mitmproxy/addonmanager.py`; middleware chain partially inferred |
| Build and Development | high | All commands found in `pyproject.toml` and `CONTRIBUTING.md` |

**Overall: medium** (1 medium, 4 high)

**Low-confidence guidance:**
- **Data Flow:** Proxy layer pipeline is inferred from `mitmproxy/proxy/server.py` and `mitmproxy/proxy/layers/`. Verify specific layer ordering by reading `mitmproxy/proxy/layers/__init__.py` and `mitmproxy/proxy/layer.py` before modifying interceptor logic.

## System Overview

mitmproxy is a Python 3.12+ interactive intercepting proxy with TLS/SSL support for HTTP/1, HTTP/2, WebSockets, TCP, UDP, and DNS. It ships three user interfaces: `mitmproxy` (terminal/curses UI), `mitmdump` (CLI flow recorder, like tcpdump for HTTP), and `mitmweb` (browser-based web UI). The core library is also usable as an addon scripting platform for building custom network inspection and manipulation tools.

**Evidence:** `pyproject.toml`, `README.md`, `mitmproxy/tools/main.py`

## Topology

- **Type:** Modular monolith with multiple CLI entry points. Single Python package with distinct sub-packages; separate TypeScript/React web frontend served via Tornado.
- **Primary areas:**
  - `mitmproxy/` — core library: proxy engine, protocol layers, addon system, flow model
  - `mitmproxy/proxy/` — asyncio proxy server, connection handling, protocol layer pipeline
  - `mitmproxy/addons/` — built-in addons (dumper, intercept, content decode, etc.)
  - `mitmproxy/tools/` — three user interfaces: console (urwid), dump, web (tornado)
  - `mitmproxy/net/` — low-level HTTP/DNS/TLS network primitives
  - `mitmproxy/contentviews/` — content rendering for different media types
  - `web/` — React + TypeScript SPA for the `mitmweb` interface
  - `test/` — pytest test suite mirroring the `mitmproxy/` package structure
  - `examples/` — addon examples and community-contributed scripts
  - `release/` — Docker image, Windows installer, binary release scripts

- **External systems:**
  - `mitmproxy_rs` Rust extension (declared in `pyproject.toml`) — WireGuard, local redirect modes, DNS over UDP
  - `aioquic` (declared in `pyproject.toml`) — HTTP/3 and QUIC support
  - `cryptography` and `pyOpenSSL` (declared in `pyproject.toml`) — TLS certificate generation and CA management
  - `tornado` (declared in `pyproject.toml`) — HTTP server for `mitmweb`
  - `urwid` (declared in `pyproject.toml`) — terminal UI for `mitmproxy` console

**Evidence:** `pyproject.toml`, `mitmproxy/proxy/server.py`, `mitmproxy/tools/main.py`, `release/docker/Dockerfile`

## Module Boundaries

| Module | Path | Responsibility | Dependencies |
|--------|------|----------------|--------------|
| Core / Flow Model | `mitmproxy/flow.py`, `mitmproxy/http.py`, `mitmproxy/dns.py`, `mitmproxy/tcp.py`, `mitmproxy/udp.py` | Domain objects: Flow, HTTPFlow, HTTPRequest, HTTPResponse, etc. | `mitmproxy/connection.py`, `mitmproxy/coretypes/` |
| Options | `mitmproxy/options.py`, `mitmproxy/optmanager.py` | Runtime configuration options management | `mitmproxy/coretypes/` |
| Addon System | `mitmproxy/addonmanager.py`, `mitmproxy/hooks.py`, `mitmproxy/command.py` | Lifecycle hook dispatch, addon registration, command system | `mitmproxy/flow.py`, `mitmproxy/options.py` |
| Master (Event Loop) | `mitmproxy/master.py` | asyncio main loop, startup/shutdown, addon coordination | `mitmproxy/addonmanager.py`, `mitmproxy/proxy/`, `mitmproxy/options.py` |
| Proxy Server | `mitmproxy/proxy/` | asyncio TCP/UDP server, connection lifecycle, layer pipeline | `mitmproxy/master.py`, `mitmproxy/net/` |
| Protocol Layers | `mitmproxy/proxy/layers/` | Stateful protocol processors: HTTP, TLS, DNS, TCP, UDP, WebSocket, QUIC | `mitmproxy/proxy/layer.py`, `mitmproxy/net/` |
| Network Primitives | `mitmproxy/net/` | HTTP/1 codec, DNS, TLS primitives, encoding | `pyproject.toml` (cryptography, h2, hyperframe) |
| Built-in Addons | `mitmproxy/addons/` | Core behaviors: intercept, dump, content decode, export, flow store | `mitmproxy/addonmanager.py`, `mitmproxy/flow.py` |
| Content Views | `mitmproxy/contentviews/` | Render flow content as human-readable text (JSON, XML, image, etc.) | `mitmproxy/flow.py` |
| User Interfaces | `mitmproxy/tools/` | Console (curses/urwid), dump (CLI), web (Tornado + React) | `mitmproxy/master.py`, `mitmproxy/addons/` |
| Web Frontend | `web/src/` | React/TypeScript SPA connecting to `mitmweb` REST+WebSocket API | `mitmproxy/tools/web/app.py` (server-side) |

**Evidence:** `mitmproxy/master.py`, `mitmproxy/proxy/server.py`, `mitmproxy/addonmanager.py`, `mitmproxy/tools/web/app.py`

## Data Flow

Primary flow: HTTP/HTTPS request intercepted by `mitmproxy` (transparent or explicit mode)

| Step | Source | Target | Message | Type | Protocol | Evidence |
|------|--------|--------|---------|------|----------|----------|
| 1 | Client | Proxy Server | TCP connection + HTTP request | sync | TCP/HTTPS | `mitmproxy/proxy/server.py` |
| 2 | Proxy Server | Protocol Layers | ConnectionMadeEvent + DataReceiveEvent | sync | function call | `mitmproxy/proxy/server.py` |
| 3 | Protocol Layers | Addon Manager | request hook (HTTPFlow) | sync | function call | `mitmproxy/proxy/layers/` |
| 4 | Addon Manager | Addons (e.g., intercept, dumper) | trigger_event(RequestHook) | sync | function call | `mitmproxy/addonmanager.py` |
| 5 | Protocol Layers | Remote Server | Forwarded HTTP request | sync | HTTPS | `mitmproxy/proxy/server.py` |
| 6 | Remote Server | Protocol Layers | HTTP response | sync | HTTPS | `mitmproxy/proxy/server.py` |
| 7 | Protocol Layers | Addon Manager | response hook (HTTPFlow) | sync | function call | `mitmproxy/proxy/layers/` |
| 8 | Protocol Layers | Client | Forwarded HTTP response | response | TCP/HTTPS | `mitmproxy/proxy/server.py` |

**Evidence:** `mitmproxy/proxy/server.py`, `mitmproxy/master.py`, `mitmproxy/addonmanager.py`

## Build and Development

- **Package manager:** uv (`uv.lock`)
- **Install / run:** `uv run mitmproxy --version` (creates `.venv` automatically)
- **Dev command:** `uv run mitmproxy` / `uv run mitmdump` / `uv run mitmweb`
- **Test runner:** pytest via tox — `uv run tox` (full suite) or `uv run pytest <path>` (targeted)
- **Lint:** `uv run tox -e lint` (runs `ruff check .`)
- **Type check:** `uv run tox -e mypy`
- **Format (fix):** `uv run tox -e fix` (runs `ruff check --fix-only` + `ruff format`)
- **Build web frontend:** `cd web && npm install && npm run build` (output goes to `web/gen/`)

**Evidence:** `CONTRIBUTING.md`, `pyproject.toml`, `uv.lock`

## Deployment

- **Docker:** `release/docker/Dockerfile` — multi-stage build producing a slim image with `mitmdump` and `mitmweb`
- **PyPI:** Released as the `mitmproxy` package via `pyproject.toml` dynamic versioning (`mitmproxy/version.py`)
- **Standalone binaries:** `release/` scripts build PyInstaller binaries for macOS, Windows, and Linux
- **CI:** GitHub Actions (`release/README.md`) — runs lint, mypy, filename_matching, individual_coverage, and pytest across Python 3.12–3.14 on Ubuntu/macOS/Windows

**Evidence:** `release/docker/Dockerfile`, `release/README.md`, `.github/workflows/main.yml`, `pyproject.toml`

## API Surface

The `mitmweb` REST API (served by `mitmproxy/tools/web/app.py` via Tornado) exposes:
- Flow management: GET/POST/PUT/DELETE on flows, replay, kill, resume, mark, comment
- Options: GET/PUT options, GET commands
- Content views: GET rendered flow content
- WebSocket: real-time flow event streaming (/updates)
- Authentication: optional HTTP Basic auth via `WebAuth` addon (`mitmproxy/tools/web/webaddons.py`)

The addon scripting API is the public Python interface for extending proxy behavior. Addons implement hook methods (`def request(flow)`, `def response(flow)`, etc.) and register with `addonmanager.AddonManager`.

**Evidence:** `mitmproxy/tools/web/app.py`, `mitmproxy/hooks.py`, `mitmproxy/addonmanager.py`
