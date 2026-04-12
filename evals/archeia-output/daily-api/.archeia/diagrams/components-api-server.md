# API Server Components

```mermaid
flowchart LR
    postgresql[("PostgreSQL<br/><i>PostgreSQL</i>")]
    redis[("Redis<br/><i>Redis</i>")]
    google-pubsub["Google Cloud Pub/Sub"]

    subgraph api-server["API Server"]
        api-auth["Auth Middleware<br/><i>TypeScript / jsonwebtoken</i>"]
        api-graphql["GraphQL Schema<br/><i>TypeScript / Mercurius / graphql</i>"]
        api-graphorm["GraphORM<br/><i>TypeScript / TypeORM</i>"]
        api-entity["Entity Layer<br/><i>TypeScript / TypeORM</i>"]
        api-common["Common Utilities<br/><i>TypeScript</i>"]
        api-integrations["Integration Clients<br/><i>TypeScript / ConnectRPC / gRPC</i>"]
        api-routes["REST Routes<br/><i>TypeScript / Fastify</i>"]
    end

    api-auth -->|"Injects user context before resolvers execute"| api-graphql
    api-graphql -->|"Uses GraphORM to build optimized TypeORM queries from GQL field selections"| api-graphorm
    api-graphql -->|"Resolvers query and mutate domain entities via TypeORM"| api-entity
    api-graphql -->|"Calls internal microservice clients for recommendations, search, and content"| api-integrations
    api-graphql -->|"Uses shared notification helpers and domain utilities"| api-common
    api-routes -->|"REST handlers read domain entities for RSS and devcards"| api-entity
    api-entity -->|"TypeORM executes SQL queries against master and read-replica"| postgresql
```

**Source:** `.archeia/codebase/architecture/components.json`
**Generated:** 2026-04-10
