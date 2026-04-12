# arq/ — Local Agent Instructions

## Module Boundaries

- `constants.py` defines all Redis key prefixes. Do not hardcode key strings in other modules — import from `constants.py`.
- `constants.py` prefixes are a shared client-worker contract. Changing any prefix breaks in-flight jobs. Never rename without a migration plan.
- `typing.py` defines all shared type aliases (`SecondsTimedelta`, `WorkerCoroutine`, `WorkerSettingsType`). Use them; do not duplicate type definitions inline.

## Async Constraints

- Do not use blocking calls inside any coroutine registered as a job function. The worker runs a single asyncio event loop — one blocking call stalls all concurrent jobs.
- All job functions must be `async def`. `worker.py` raises `RuntimeError` if a non-coroutine is registered.

## Serialisation Rule

- Default serialiser is pickle. If adding or modifying a custom serialiser path, both the client (`ArqRedis.__init__`) and the worker (`Worker.__init__`) must receive matching `job_serializer`/`job_deserializer` callables.

## py.typed

- `arq/py.typed` is a zero-byte PEP 561 marker. Do not delete or modify it. Removing it breaks downstream type checking for consumers.

## Redis Key Naming

- All queue/result/in-progress keys use prefixes from `constants.py`. Do not write to Redis directly using strings — always compose keys from the imported constants.

## README Maintenance

Before working in this directory, read `arq/README.md`.
After completing work, update the Learnings section with anything non-obvious discovered.

Maintains: `arq/README.md`
