# scripts

Operational and maintenance scripts for the Polar backend. Contains database management, data migration, seed loading, and deployment helpers.

## Key Concepts

- **Database scripts** -- `db.py` wraps Alembic commands: `upgrade`, `recreate`, `reparent` (fix conflicting migrations). Run via `uv run python -m scripts.db`.
- **Seed data** -- `seeds_load.py` populates the database with sample data for development.
- **Tinybird** -- `tinybird.py` deploys Tinybird datasource definitions.
- **Load test setup** -- `loadtest_setup.py` prepares data for event ingestion load tests.

## Usage

All scripts are invoked via `uv run python -m scripts.{name}` or via taskipy tasks defined in `pyproject.toml` (e.g., `uv run task db_migrate`, `uv run task seeds_load`).

## Learnings

_No learnings recorded yet._
