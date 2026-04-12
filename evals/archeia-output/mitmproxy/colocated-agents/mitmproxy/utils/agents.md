## utils — Local Agent Instructions

- Never call `asyncio.create_task(...)` directly anywhere in `mitmproxy/utils/asyncio_utils.py` or its callers. Use `asyncio_utils.create_task(coro, name=..., keep_ref=...)` instead. The TID251 lint rule enforces this; direct usage causes task GC mid-execution. The `# noqa: TID251` comment in `asyncio_utils.py` is the one allowed exception.
- `utils/` must remain a leaf package — do not add imports from `mitmproxy/addons/`, `mitmproxy/tools/`, or `mitmproxy/proxy/`. These packages import from `utils/`; circular imports will break startup.
- `signals.py` uses synchronous dispatch (`SyncSignal`). Do not add async callbacks to signal handlers.
- `asyncio_utils.set_eager_task_factory()` is a context manager; always use it in a `with` block.

## README Maintenance

Before working in this directory, read `mitmproxy/utils/README.md`.
After completing work, update the README's Learnings section with anything non-obvious discovered.

Maintains: `mitmproxy/utils/README.md`
