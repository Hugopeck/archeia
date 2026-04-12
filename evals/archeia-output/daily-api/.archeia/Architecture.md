# Architecture

## Overview

Daily API is a TypeScript/Node.js backend service that powers the daily.dev developer news feed and community platform. It exposes a primary GraphQL API (via Fastify + Mercurius) alongside REST-style routes for RSS, webhooks, devcards, and public endpoints. A background processor runs independently, subscribing to Google Cloud Pub/Sub topics for event-driven work. Scheduled cron jobs and Temporal workflows handle periodic and long-running tasks.

**Evidence:** `src/index.ts`, `src/background.ts`, `src/cron.ts`, `README.md`

## Topology

The service runs as multiple deployable processes from a single codebase:

| Process | Entry | Description |
|---------|-------|-------------|
| API server | `bin/cli api` → `src/index.ts` | Fastify HTTP server with Mercurius GraphQL |
| Background worker | `bin/cli background` → `src/background.ts` | Google Pub/Sub subscription handlers |
| Personalized digest | `bin/cli personalized-digest` | Subset of background workers for digests |
| Cron runner | `bin/cli worker-job` | Runs individual cron handlers by name |
| Temporal worker | `src/temporal/notifications/index.ts` | Temporal workflow worker for notification delivery |

**Evidence:** `package.json` (scripts), `src/index.ts`, `src/background.ts`, `src/cron.ts`, `src/temporal/notifications/index.ts`

<!-- INSUFFICIENT EVIDENCE: runtime units for Containers.json -->

## Module Boundaries

| Module | Path | Responsibility |
|--------|------|----------------|
| entity | `src/entity/` | TypeORM entity definitions for all domain models |
| schema | `src/schema/` | GraphQL type definitions and resolvers (Apollo/Mercurius) |
| workers | `src/workers/` | Pub/Sub message handlers for background events |
| routes | `src/routes/` | Fastify REST route handlers (RSS, webhooks, devcards, boot, etc.) |
| common | `src/common/` | Shared utilities, notification helpers, mailing, integrations |
| integrations | `src/integrations/` | External service clients (bragi, freyja, snotra, mimir, linear, anthropic, skadi, lofn, feed) |
| cron | `src/cron/` | Scheduled job handlers |
| migration | `src/migration/` | TypeORM database migration files (479 files) |
| graphorm | `src/graphorm/` | Internal GraphQL-ORM bridge layer |
| temporal | `src/temporal/` | Temporal workflow and activity definitions |
| notifications | `src/notifications/` | Notification builder utilities |
| directive | `src/directive/` | Custom GraphQL schema directives |
| telemetry | `src/telemetry/` | OpenTelemetry instrumentation |
| compatibility | `src/compatibility/` | Legacy API v1 backwards-compatible Fastify routes |

**Evidence:** `src/entity/index.ts`, `src/workers/index.ts`, `src/routes/index.ts`, `README.md`

<!-- INSUFFICIENT EVIDENCE: Containers.json unavailable for Components.json -->

## Data Flow

Primary request path (GraphQL query):

| Step | From | To | Protocol |
|------|------|----|----------|
| 1 | Client | Fastify (src/index.ts) | HTTPS |
| 2 | Fastify | Auth middleware (src/auth.ts) | function call |
| 3 | Fastify | Mercurius GraphQL engine | function call |
| 4 | Mercurius | GraphQL resolvers (src/schema/) | function call |
| 5 | Resolvers | TypeORM entities (src/entity/) | function call |
| 6 | TypeORM | PostgreSQL (master or replica) | SQL |
| 7 | Resolvers | Redis cache (src/redis.ts) | Redis |
| 8 | Resolvers | External integrations (src/integrations/) | HTTPS/gRPC |
| 9 | Fastify | Client | HTTPS response |

Background event path:

| Step | From | To | Protocol |
|------|------|----|----------|
| 1 | Google Pub/Sub | Worker subscriber (src/background.ts) | message queue |
| 2 | Worker subscriber | Individual worker handlers (src/workers/) | function call |
| 3 | Worker handler | PostgreSQL | SQL |
| 4 | Worker handler | Redis | Redis |
| 5 | Worker handler | External services (CIO, OneSignal, Slack, etc.) | HTTPS |

**Evidence:** `src/index.ts`, `src/background.ts`, `src/data-source.ts`, `src/redis.ts`

<!-- INSUFFICIENT EVIDENCE: primary interaction flow for DataFlow.json -->

## Data Model

Key domain entities defined in `src/entity/`:

- **User** — platform user with authentication, streak, achievements, personalized digest settings
- **Post** (discriminated: ArticlePost, SharePost, FreeformPost, WelcomePost, CollectionPost, YouTubePost, SocialTwitterPost) — content items in the feed
- **Source** — content sources (publishers, squads) with members
- **Comment** — threaded user comments on posts
- **Feed / FeedSource / FeedTag** — user feed configuration and filters
- **Bookmark / BookmarkList** — saved posts
- **Notification** — in-app notification records
- **Organization / UserCompany** — company and organizational affiliation
- **UserStreak / Achievement** — gamification and engagement tracking
- **View** — post view tracking

**Evidence:** `src/entity/index.ts`, `src/entity/user/index.ts`, `src/entity/posts/index.ts`

## State Lifecycles

<!-- INSUFFICIENT EVIDENCE: no explicit state machine libraries or clear enum+transition patterns confirmed -->

## External Systems

| System | Role | Evidence |
|--------|------|---------|
| PostgreSQL | Primary relational database (master/replica) | `src/data-source.ts` |
| Redis | Cache, Pub/Sub relay, rate limiting | `src/redis.ts`, `package.json` |
| Google Cloud Pub/Sub | Async event bus between API and background workers | `src/background.ts` |
| ClickHouse | Analytics event storage | `clickhouse/migrations/`, `package.json` (@clickhouse/client) |
| Temporal | Durable workflow orchestration for notifications | `src/temporal/`, `package.json` (@temporalio/*) |
| Cloudinary | Image storage and transformation | `package.json` (cloudinary) |
| Customer.io | User marketing and transactional email | `src/cio.ts`, `package.json` (customerio-node) |
| OneSignal | Push notification delivery | `src/onesignal.ts`, `package.json` (@onesignal/node-onesignal) |
| GrowthBook | Feature flagging and A/B testing | `src/growthbook.ts`, `package.json` (@growthbook/growthbook) |
| Paddle | Subscription billing | `src/paddle.ts`, `package.json` (@paddle/paddle-node-sdk) |
| Slack | Internal team notifications | `package.json` (@slack/web-api, @slack/webhook) |
| MeiliSearch | Full-text search (local dev) | `docker-compose.yml` (getmeili/meilisearch) |
| BigQuery | Analytics data warehouse | `package.json` (@google-cloud/bigquery) |
| Freyja | Internal AI/media service (proxied at /freyja) | `src/index.ts` (proxy config) |

## Tech Stack

- **Runtime:** Node.js 22 (`.nvmrc`)
- **Language:** TypeScript 5.x (`tsconfig.json`)
- **HTTP framework:** Fastify 5.x (`package.json`)
- **GraphQL:** Mercurius 16.x + graphql 16.x (`package.json`)
- **ORM:** TypeORM 0.3.28 (`package.json`, `src/data-source.ts`)
- **Package manager:** pnpm 9.14.4 (`package.json`)
- **Test framework:** Jest 29.x (`jest.config.js`)
- **Observability:** OpenTelemetry (traces + metrics via gRPC export) (`package.json`)
- **Workflow engine:** Temporal 1.14.x (`src/temporal/`)
