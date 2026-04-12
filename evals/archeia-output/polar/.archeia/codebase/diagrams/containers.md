# Container Diagram

```mermaid
flowchart TB
    MERCHANT([Merchant])
    CUSTOMER([Customer])

    subgraph boundary["Polar"]
        API["API Server<br/><i>Python / FastAPI / Uvicorn</i>"]
        WORKER["Background Worker<br/><i>Python / Dramatiq / Redis</i>"]
        WEB["Web Dashboard<br/><i>TypeScript / Next.js / React</i>"]
        BO["Backoffice<br/><i>Python / FastAPI / HTMX / DaisyUI</i>"]
        EMAIL["Email Renderer<br/><i>TypeScript / Node.js</i>"]
    end

    STRIPE["Stripe<br/><i>Stripe API v14</i>"]
    GITHUB["GitHub<br/><i>GitHub API via githubkit</i>"]
    POSTGRESQL[("PostgreSQL<br/><i>PostgreSQL via asyncpg + SQLAlchemy</i>")]
    REDIS[("Redis")]
    S3["S3-compatible Storage<br/><i>AWS S3 / MinIO via boto3</i>"]

    MERCHANT -->|"Manages products, views analytics"| WEB
    CUSTOMER -->|"Accesses customer portal"| WEB
    MERCHANT -->|"Integrates via REST API"| API
    WEB -->|"Fetches data and submits actions via REST API."| API
    API -->|"Reads and writes all business entities."| POSTGRESQL
    API -->|"Enqueues background jobs and caches data."| REDIS
    API -->|"Stores and retrieves files."| S3
    API -->|"Creates payment intents, manages subscriptions."| STRIPE
    API -->|"Authenticates users via OAuth."| GITHUB
    WORKER -->|"Consumes jobs from Dramatiq queues."| REDIS
    WORKER -->|"Reads and writes data during job processing."| POSTGRESQL
    WORKER -->|"Processes payment callbacks."| STRIPE
    BO -->|"Queries data for admin views."| POSTGRESQL
```

**Source:** `.archeia/codebase/architecture/containers.json`
**Generated:** 2026-04-09
