# Background Worker Components

```mermaid
flowchart LR
    postgresql[("PostgreSQL<br/><i>PostgreSQL</i>")]
    google-pubsub["Google Cloud Pub/Sub"]

    subgraph background-worker["Background Worker"]
        worker-handlers["Worker Handlers<br/><i>TypeScript</i>"]
        worker-notifications["Notification Workers<br/><i>TypeScript</i>"]
    end

    api-entity["Entity Layer<br/><i>TypeScript / TypeORM</i>"]

    worker-handlers -->|"Subscribes to domain event topics"| google-pubsub
    worker-handlers -->|"Workers share entity definitions to query the same database"| api-entity
    api-entity -->|"TypeORM executes SQL"| postgresql
```

**Source:** `.archeia/codebase/architecture/components.json`
**Generated:** 2026-04-10
