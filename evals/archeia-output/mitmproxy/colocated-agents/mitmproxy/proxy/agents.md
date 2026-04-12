## proxy — Local Agent Instructions

- Addons must never import directly from `mitmproxy/proxy/`. Interaction with the proxy subsystem happens only through hook events fired by `addonmanager.py`. Importing proxy internals from an addon will bypass the hook lifecycle.
- Layers are Python generators using the Command/Event pattern (`layer.py`). A layer yields `Command` objects and receives `Event` objects. Do not call layer methods directly — drive them via the `send()` protocol in `server.py`.
- `Context` is per-connection state. Do not share a `Context` instance across connections or store it on a long-lived object.
- `mode_specs.py` uses dataclasses for mode parsing. When adding a new proxy mode, add both a spec class in `mode_specs.py` and a server in `mode_servers.py`.
- Layer stacking order matters: TLS layers must wrap protocol layers (e.g., `ClientTLS → HTTP`). Inserting a layer in the wrong position silently breaks protocol detection.

## README Maintenance

Before working in this directory, read `mitmproxy/proxy/README.md`.
After completing work, update the README's Learnings section with anything non-obvious discovered.

Maintains: `mitmproxy/proxy/README.md`
