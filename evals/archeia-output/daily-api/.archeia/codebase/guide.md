# Guide

## Prerequisites

- Node.js 22 (use `.nvmrc` with nvm: `nvm use`)
- pnpm 9.14.4 (`corepack enable && corepack prepare`)
- Docker and Docker Compose (for local dependencies)

**Evidence:** `.nvmrc`, `package.json`

## Setup

```bash
# 1. Start local dependencies (PostgreSQL, Redis, MeiliSearch)
docker-compose up -d

# 2. Install dependencies
pnpm install

# 3. Apply database migrations
pnpm run db:migrate:latest

# 4. (Optional) Load seed data
pnpm run db:seed:import
```

**Evidence:** `README.md`, `docker-compose.yml`, `package.json`

## Environment Variables

Copy `.env` and fill in required values. Key variables:

| Variable | Purpose |
|----------|---------|
| `TYPEORM_HOST` | PostgreSQL host |
| `TYPEORM_USERNAME` | PostgreSQL user |
| `TYPEORM_PASSWORD` | PostgreSQL password |
| `TYPEORM_DATABASE` | PostgreSQL database name |
| `TYPEORM_READ_HOST` | PostgreSQL read-replica host |
| `REDIS_HOST` | Redis host |
| `REDIS_PORT` | Redis port |
| `REDIS_PASS` | Redis password |
| `ACCESS_SECRET` | JWT signing secret for auth |
| `COOKIES_KEY` | Cookie signing secret |
| `FREYJA_ORIGIN` | Upstream Freyja service URL |

**Evidence:** `.env`, `src/data-source.ts`, `src/redis.ts`, `src/index.ts`

## Dev Commands

```bash
# Run the API server (port 5000)
pnpm run dev

# Run the background worker
pnpm run dev:background

# Run the personalized digest worker
pnpm run dev:personalized-digest

# Run the Temporal worker
pnpm run dev:temporal-worker

# Run a cron job by name
pnpm run dev:worker-job
```

**Evidence:** `package.json`

## Build

```bash
pnpm run build
```

Compiles TypeScript to `build/`, copies `ormconfig.js`, `package.json`, `pnpm-lock.yaml`, and `seeds/`.

**Evidence:** `package.json`

## Testing

Tests require a running PostgreSQL database (`api_test` database).

```bash
# Run all tests (resets the test database first)
pnpm run test

# Tests run serially (--runInBand) with NODE_ENV=test
```

Test files are in `__tests__/`. The `pretest` script drops and reapplies all migrations against `api_test`.

**Evidence:** `package.json`, `jest.config.js`

## Database Operations

```bash
# Apply pending migrations
pnpm run db:migrate:latest

# Rollback last migration
pnpm run db:migrate:rollback

# Generate a new migration from entity changes
pnpm run db:migrate:make

# Create an empty migration file
pnpm run db:migrate:create

# Drop schema
pnpm run db:schema:drop

# Reset (drop + remigrate)
pnpm run db:migrate:reset
```

**Evidence:** `package.json`, `src/data-source.ts`

## ClickHouse Migrations

```bash
# Run ClickHouse migrations
pnpm run bin/runClickhouseMigrations.ts

# Create a new ClickHouse migration
pnpm run bin/createClickhouseMigration.ts
```

**Evidence:** `clickhouse/migrations/`, `bin/runClickhouseMigrations.ts`

## Linting

```bash
pnpm run lint
```

Runs ESLint with max-warnings 0. Must pass before merging.

**Evidence:** `package.json`, `.eslintrc.js`

## Production Start

```bash
# API server
pnpm run start

# Background worker
pnpm run start:background
```

**Evidence:** `package.json`

## Temporal (Local)

```bash
# Start local Temporal server
pnpm run dev:temporal-server

# Start Temporal worker
pnpm run dev:temporal-worker
```

**Evidence:** `package.json`
