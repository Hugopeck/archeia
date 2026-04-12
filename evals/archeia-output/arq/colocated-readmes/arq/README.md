# arq

Core library package. Implements the full job queue: connection management, job lifecycle, worker execution loop, cron scheduling, and the CLI entrypoint.

## Structure

```mermaid
graph LR
    CLI[cli.py<br/>Click entrypoint] --> W[worker.py<br/>Worker loop]
    APP[Application code] --> CONN[connections.py<br/>ArqRedis / create_pool]
    CONN --> |enqueue_job ZADD| REDIS[(Redis)]
    W --> |ZRANGEBYSCORE poll| REDIS
    W --> |WATCH/MULTI claim| REDIS
    W --> |SET result| REDIS
    CONN --> JOBS[jobs.py<br/>JobDef / JobResult]
    W --> JOBS
    W --> CRON[cron.py<br/>CronJob / next_cron]
    W --> CONST[constants.py<br/>key prefixes]
    W --> UTILS[utils.py<br/>poll / time helpers]
```

## Key Concepts

- **ArqRedis is a Redis subclass** — `connections.py` extends `redis.asyncio.Redis` to add `enqueue_job`. Do not bypass it to write to queue keys directly.
- **Sorted set as queue** — Jobs are stored in Redis sorted sets with score = UNIX timestamp milliseconds. Deferred jobs have a future score; due jobs score ≤ now.
- **Atomic claim via WATCH/MULTI** — `worker.py` uses Redis optimistic locking to claim a job exactly once across concurrent workers. Two workers polling simultaneously will not both execute the same job.
- **Pluggable serialisation** — Default is pickle; pass `job_serializer`/`job_deserializer` callables to `ArqRedis` (e.g., msgpack). Both the enqueuing client and the worker must use the same serialiser.
- **`constants.py` key prefixes are a shared contract** — `job_key_prefix`, `in_progress_key_prefix`, `result_key_prefix` etc. are used by both client and worker; changing them breaks in-flight jobs.

## Usage

`connections.py` is the public API for application code: `create_pool(RedisSettings(...))` returns an `ArqRedis` instance. `worker.py` exports `Worker`, `run_worker`, and `create_worker` for process lifecycle. `cli.py` wraps these for command-line invocation.

See [Guide.md](../.archeia/codebase/guide.md) for dev commands.

## Learnings

_Seed entry — append discoveries here as you work._
