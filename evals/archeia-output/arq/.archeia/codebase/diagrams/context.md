# System Context

```mermaid
flowchart TB
    developer(["Library Consumer<br/><i>Developer</i>"])
    ops(["Operator<br/><i>CLI / CI</i>"])

    subgraph boundary["arq"]
        arq["arq<br/><i>Python asyncio job queue<br/>library backed by Redis</i>"]
    end

    redis[("Redis<br/><i>Redis 5/6/7</i>")]
    pypi["PyPI<br/><i>Package registry</i>"]
    netlify["Netlify<br/><i>Docs hosting</i>"]

    developer -- "imports to enqueue jobs and configure workers" --> arq
    ops -- "runs arq CLI to start workers and check health" --> arq
    arq -- "reads and writes job data via sorted sets and key-TTL patterns" --> redis
    arq -- "published on version tag via GitHub Actions" --> pypi
    arq -- "documentation site deployed via make publish-docs" --> netlify
```

**Source:** `.archeia/codebase/architecture/system.json`
**Generated:** 2026-04-10
