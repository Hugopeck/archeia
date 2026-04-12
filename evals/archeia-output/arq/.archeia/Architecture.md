# Architecture

> arq — Python asyncio job queue backed by Redis

**Evidence:** `pyproject.toml`, `README.md`, `arq/__init__.py`

## System Overview

arq is a Python library that provides distributed job queuing using asyncio and Redis. Application code enqueues jobs by calling functions on `ArqRedis` (an extended Redis client). A long-running `Worker` process polls Redis sorted sets, deserialises job payloads, executes the async coroutines, and writes results back to Redis. A CLI (`arq <WorkerSettings>`) wraps worker lifecycle management.

**Evidence:** `arq/connections.py`, `arq/worker.py`, `arq/cli.py`

## Topology

This is a single-package Python library distributed via PyPI. At runtime it produces two process types:

1. **Application process** — imports `arq.connections.ArqRedis` / `arq.connections.create_pool` to enqueue jobs.
2. **Worker process** — instantiated via `arq.worker.Worker` or the `arq` CLI; long-running asyncio loop polling Redis queues.

Both communicate exclusively through a shared Redis instance. There is no direct network link between application and worker.

<!-- INSUFFICIENT EVIDENCE: runtime units for Containers.json -->

**Evidence:** `arq/connections.py`, `arq/worker.py`, `arq/cli.py`

## Module Boundaries

| Module              | Responsibility                                                                 |
|---------------------|--------------------------------------------------------------------------------|
| `arq/connections.py` | `RedisSettings`, `ArqRedis` (Redis subclass), `create_pool`, job enqueue API |
| `arq/worker.py`     | `Worker` class, `Function` wrapper, job execution loop, health check, cron scheduling |
| `arq/jobs.py`       | `Job`, `JobDef`, `JobResult`, `JobStatus` enum, serialisation helpers         |
| `arq/cron.py`       | `CronJob`, `next_cron` datetime calculator                                    |
| `arq/cli.py`        | Click CLI entrypoint; delegates to `worker.run_worker`, `worker.check_health` |
| `arq/constants.py`  | Redis key prefixes and default values shared across modules                   |
| `arq/utils.py`      | `import_string`, time conversion helpers, `poll` async generator              |
| `arq/typing.py`     | Type aliases (`SecondsTimedelta`, `WorkerCoroutine`, `WorkerSettingsType`)    |
| `arq/logs.py`       | `default_log_config` dict for logging configuration                          |

<!-- INSUFFICIENT EVIDENCE: Containers.json unavailable for Components.json -->

**Evidence:** `arq/connections.py`, `arq/worker.py`, `arq/jobs.py`, `arq/cron.py`, `arq/cli.py`, `arq/constants.py`

## Data Flow

Primary flow — enqueue and execute a job:

| Step | From                  | To                    | Protocol    | Description                                    |
|------|-----------------------|-----------------------|-------------|------------------------------------------------|
| 1    | Application code      | ArqRedis              | function call | Call `arq_redis.enqueue_job('fn_name', *args)` |
| 2    | ArqRedis              | Redis                 | Redis ZADD   | Serialise `JobDef` and add to queue sorted set |
| 3    | Worker poll loop      | Redis                 | Redis ZRANGEBYSCORE | Check for due jobs by score (timestamp ms) |
| 4    | Worker                | Redis                 | Redis WATCH/MULTI | Atomically claim job with in-progress key  |
| 5    | Worker                | User coroutine        | function call | Execute registered async function              |
| 6    | Worker                | Redis                 | Redis SET    | Write `JobResult` to result key with TTL       |
| 7    | Application code      | Redis (via `Job`)     | Redis GET    | Poll or await job result                       |

<!-- INSUFFICIENT EVIDENCE: primary interaction flow for DataFlow.json -->

**Evidence:** `arq/connections.py`, `arq/worker.py`, `arq/jobs.py`

## Data Model

No ORM or database schema files detected. Domain data structures are Python dataclasses serialised to Redis via pickle (default) or a pluggable serialiser.

| Class       | Module           | Key Fields                                                          |
|-------------|------------------|---------------------------------------------------------------------|
| `RedisSettings` | connections.py | host, port, database, ssl, sentinel, retry settings              |
| `JobDef`    | jobs.py          | function (str), args, kwargs, job_try, enqueue_time, score, job_id |
| `JobResult` | jobs.py          | extends JobDef; adds success (bool), result (Any), start_time, finish_time, queue_name |
| `JobStatus` | jobs.py          | Enum: deferred, queued, in_progress, complete, not_found          |
| `Function`  | worker.py        | name, coroutine, timeout_s, keep_result_s, keep_result_forever, max_tries |
| `CronJob`   | cron.py          | month, day, weekday, hour, minute, second schedule fields          |

**Evidence:** `arq/jobs.py`, `arq/connections.py`, `arq/worker.py`, `arq/cron.py`

## State Lifecycles

`JobStatus` defines the lifecycle of a queued job:

```
deferred → queued → in_progress → complete
                                → not_found (if result TTL expires)
```

States are stored as Redis key patterns (not a relational column). The worker transitions jobs from queued → in_progress atomically using Redis WATCH/MULTI.

**Evidence:** `arq/jobs.py`, `arq/worker.py`

## Key Design Decisions

- **Redis-only transport** — No broker abstraction; Redis sorted sets are the queue. Score = UNIX timestamp milliseconds for deferred scheduling.
- **Pluggable serialisation** — Default is pickle; callers can pass custom `Serializer`/`Deserializer` callables (e.g., msgpack, as shown in `docs/examples/`).
- **Asyncio-native** — All worker execution is async; the worker runs a single asyncio event loop.
- **Sentinel support** — `RedisSettings.sentinel = True` switches connection to Redis Sentinel for HA.
- **No ORM** — No database. All state lives in Redis with key-prefix namespacing defined in `arq/constants.py`.

**Evidence:** `arq/connections.py`, `arq/jobs.py`, `arq/worker.py`, `arq/constants.py`
