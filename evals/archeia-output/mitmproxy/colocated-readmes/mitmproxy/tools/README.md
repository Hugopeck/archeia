# tools

The three user interfaces for mitmproxy: console (terminal/curses), dump (CLI), and web (browser). Each interface wires a `Master` instance with a set of addons specific to that UI's mode.

## Structure

```mermaid
graph LR
    Main[main.py run()] -->|creates| ConsoleMaster[console/master.py]
    Main -->|creates| DumpMaster[dump.py DumpMaster]
    Main -->|creates| WebMaster[web/master.py WebMaster]
    ConsoleMaster -->|urwid TUI| Console[console/ UI widgets]
    DumpMaster -->|stdout| Dumper[mitmproxy/addons/dumper.py]
    WebMaster -->|serves| WebApp[web/app.py Tornado]
    WebApp -->|static assets| Frontend[mitmproxy/tools/web/static/]
    WebApp -->|WebSocket| Browser[browser client]
```

## Key Concepts

- **`main.py:run()`** — shared entry point factory. Takes a `Master` class, argument parser factory, and optional extra arg handler. Creates the asyncio event loop, instantiates the Master, and runs it. All three interfaces use this.
- **Console** (`console/`) — full curses/urwid TUI. Key bindings, flow list, detail view, hex viewer, and interactive intercept editor. Heavy: do not import in test environments without urwid.
- **Dump** (`dump.py`) — `DumpMaster` with `Dumper` addon attached. The `--save-stream-file` and `--read-flow-file` options are handled here.
- **Web** (`web/`) — `WebMaster` + Tornado HTTP server. `app.py` implements the REST API and WebSocket relay. `webaddons.py` provides optional HTTP Basic auth (`WebAuth`) and static asset serving (`StaticViewer`).
- **`cmdline.py`** — shared argparse setup for all three CLI entry points. Option loading order: defaults → config file → env vars → CLI args.

## Usage

Entry points defined in `pyproject.toml` `[project.scripts]`: `mitmproxy → tools.main:mitmproxy`, `mitmdump → tools.main:mitmdump`, `mitmweb → tools.main:mitmweb`.

**Evidence:** `mitmproxy/tools/main.py`, `mitmproxy/tools/web/app.py`, `mitmproxy/tools/dump.py`

## Learnings

<!-- Add learnings here as you work in this directory. -->
