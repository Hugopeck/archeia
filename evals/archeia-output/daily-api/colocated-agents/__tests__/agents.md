# agents.md — `__tests__/`

## Rules

- Tests require a live PostgreSQL connection — there is no in-memory database. Run `docker-compose up -d` before testing.
- `pnpm run test` runs `pretest` automatically (drops and remigrates `api_test`). Never skip this when running the full suite.
- Run individual tests with: `NODE_ENV=test npx jest __tests__/specific-test.ts --testEnvironment=node --runInBand`
- Always include `--runInBand` for database-dependent tests — parallel workers cause DB contention.
- `TZ=UTC` is forced. All date assertions must assume UTC, not local system timezone.
- Use fixture helpers from `__tests__/fixture/` to create test data — do not write raw `INSERT` statements. Extend existing helpers rather than duplicating.
- `jest.resetAllMocks()` in `beforeEach` — always call this before each test to prevent mock state leakage.
- Test files matching `__tests__/.*/helpers.ts` and `__tests__/fixture/` are excluded from jest test execution (see `jest.config.js`). They are utilities only.
- Type errors from `ts-jest` are suppressed during tests — rely on `pnpm build` or your editor for TypeScript feedback.

## README Maintenance

Before working in `__tests__/`, read `__tests__/README.md`.
After completing work, update the README's Learnings section with anything non-obvious discovered.

Maintains: `__tests__/README.md`
