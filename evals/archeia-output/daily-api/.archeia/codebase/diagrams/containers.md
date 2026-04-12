# Container Diagram

```mermaid
flowchart LR
    authenticated-user([Authenticated User])
    anonymous-user([Anonymous User])

    subgraph boundary["Daily API"]
        api-server["API Server<br/><i>Node.js 22 / TypeScript / Fastify 5 / Mercurius GraphQL</i>"]
        background-worker["Background Worker<br/><i>Node.js 22 / TypeScript / Google Cloud Pub/Sub</i>"]
        cron-runner["Cron Runner<br/><i>Node.js 22 / TypeScript</i>"]
        temporal-worker["Temporal Worker<br/><i>Node.js 22 / TypeScript / Temporal SDK 1.14</i>"]
    end

    postgresql[("PostgreSQL<br/><i>PostgreSQL 18</i>")]
    redis[("Redis<br/><i>Redis Stack 7.2</i>")]
    google-pubsub["Google Cloud Pub/Sub<br/><i>Google Cloud Pub/Sub</i>"]
    clickhouse[("ClickHouse<br/><i>ClickHouse</i>")]
    temporal["Temporal<br/><i>Temporal 1.14</i>"]
    customer-io["Customer.io<br/><i>Customer.io</i>"]
    onesignal["OneSignal<br/><i>OneSignal</i>"]

    authenticated-user -->|"Sends GraphQL queries and mutations over HTTPS"| api-server
    anonymous-user -->|"Reads public feed content over HTTPS"| api-server
    api-server -->|"Reads and writes domain entities via TypeORM"| postgresql
    api-server -->|"Caches resolver results and relays GraphQL subscriptions"| redis
    api-server -->|"Publishes domain events to trigger background workers"| google-pubsub
    api-server -->|"Writes post view and analytics events"| clickhouse
    api-server -->|"Schedules notification workflows"| temporal
    background-worker -->|"Subscribes to domain event topics"| google-pubsub
    background-worker -->|"Reads and writes domain data during event processing"| postgresql
    background-worker -->|"Updates cached counters and triggers real-time events"| redis
    background-worker -->|"Syncs user lifecycle events for emails"| customer-io
    background-worker -->|"Delivers push notifications on user events"| onesignal
    cron-runner -->|"Reads and updates data for scheduled maintenance tasks"| postgresql
    temporal-worker -->|"Polls for and executes workflow tasks"| temporal
    temporal-worker -->|"Executes notification activities that read user and notification data"| postgresql
```

**Source:** `.archeia/codebase/architecture/containers.json`
**Generated:** 2026-04-10
