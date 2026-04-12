# tests/ — Local Agent Instructions

## Redis Requirement

- Tests use a real Redis instance via testcontainers. Docker must be running before executing tests.
- Do not mock Redis in tests. The test suite validates actual Redis behaviour (WATCH/MULTI atomicity, TTL expiry, sorted set scoring).

## Fixture Usage

- `arq_redis` — provides a flushed `ArqRedis` instance per test. Always use this fixture, not a manually created connection.
- `worker` — factory fixture; call it with `functions=[...]` to create a `Worker` in burst mode. Do not construct `Worker` directly in tests.
- `env` — use for setting/cleaning environment variables. It restores original state after the test.
- All fixtures are in `conftest.py`. Do not duplicate fixture logic in individual test files.

## Asyncio Convention

- `asyncio_mode = 'auto'` is configured. Do not add `@pytest.mark.asyncio` — it is not needed and causes warnings.

## Redis Version

- Set `ARQ_TEST_REDIS_VERSION` to test against a specific Redis version (e.g., `ARQ_TEST_REDIS_VERSION=7 make test`).
- CI tests against Redis 5, 6, and 7. New tests must not rely on features unavailable in Redis 5.

## Test Timeout

- Tests have a 10-second timeout (`timeout = 10` in pyproject.toml). Long-running scenarios must use burst mode or mock time.

## README Maintenance

Before working in this directory, read `tests/README.md`.
After completing work, update the Learnings section with anything non-obvious discovered.

Maintains: `tests/README.md`
