# tinybird

Tinybird analytics configuration for real-time event processing and usage-based billing. Contains datasource definitions, transformation pipes, and API endpoints.

## Key Concepts

- **Datasources** -- `datasources/` defines the schema for event data ingested into Tinybird (15 datasource files).
- **Pipes** -- `pipes/` contains transformation and aggregation pipelines (21 pipe files).
- **Endpoints** -- `endpoints/` exposes query results as HTTP APIs for the Polar dashboard and billing system.
- **Usage metering** -- Tinybird powers the usage-based billing meter system, aggregating customer events for billing calculations.

## Usage

Deployed via `uv run task tb_deploy` (from `server/`). The `integrations/tinybird/` module sends events to Tinybird. Meter queries are consumed by `meter/` and `customer_meter/` modules.

## Learnings

_No learnings recorded yet._
