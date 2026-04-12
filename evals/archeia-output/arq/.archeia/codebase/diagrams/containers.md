# Container Diagram

```mermaid
flowchart TB
    developer(["Library Consumer<br/><i>Developer</i>"])
    ops(["Operator<br/><i>CLI / CI</i>"])

    subgraph boundary["arq"]
        client["Application / Client<br/><i>Python asyncio, arq.connections.ArqRedis</i>"]
        worker["Worker Process<br/><i>Python asyncio, arq.worker.Worker</i>"]
    end

    redis[("Redis<br/><i>Redis 5/6/7</i>")]

    developer -- "embeds ArqRedis to enqueue jobs" --> client
    ops -- "invokes arq CLI to start and manage workers" --> worker
    client -- "enqueues jobs via ZADD; reads results via GET" --> redis
    worker -- "polls ZRANGEBYSCORE; claims via WATCH/MULTI; writes results via SET" --> redis
```

**Source:** `.archeia/codebase/architecture/containers.json`
**Generated:** 2026-04-10
