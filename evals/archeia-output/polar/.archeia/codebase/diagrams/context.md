# System Context

```mermaid
flowchart TB
    subgraph boundary["Polar"]
        POLAR["Polar<br/><i>Python / FastAPI + Next.js</i>"]
    end

    MERCHANT([Merchant])
    CUSTOMER([Customer])
    STRIPE["Stripe<br/><i>Stripe API v14</i>"]
    GITHUB["GitHub<br/><i>GitHub API via githubkit</i>"]
    POSTGRESQL[("PostgreSQL<br/><i>PostgreSQL via asyncpg + SQLAlchemy</i>")]
    REDIS[("Redis")]
    S3["S3-compatible Storage<br/><i>AWS S3 / MinIO via boto3</i>"]

    MERCHANT -->|"Manages products, subscriptions, and views analytics via the web dashboard."| POLAR
    CUSTOMER -->|"Purchases products and manages subscriptions via checkout and customer portal."| POLAR
    POLAR -->|"Processes payments, manages subscriptions, and handles payouts."| STRIPE
    POLAR -->|"Authenticates users via OAuth and grants repository access as a benefit."| GITHUB
    POLAR -->|"Stores and retrieves all business data."| POSTGRESQL
    POLAR -->|"Queues background jobs and caches transient data."| REDIS
    POLAR -->|"Stores uploaded files, invoices, and downloadable content."| S3
```

**Source:** `.archeia/codebase/architecture/system.json`
**Generated:** 2026-04-09
