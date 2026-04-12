# agents.md — packages/sdk/

## Test Runner

The SDK uses Node.js native test runner (`node --test`), NOT vitest. Tests live in `tests/integration/broker/`. Do not add vitest test files here — `vitest.config.ts` explicitly excludes `packages/sdk/**`.

Run SDK tests:
```bash
npm run test:integration:broker
```

## Exports Are Contractual

`packages/sdk/src/index.ts` is a public API surface. Adding or removing exports is a breaking change. Do not delete existing exports without a major version bump. Changes to `protocol.ts` types must remain backward compatible.

## Build Before Test

The SDK must be built before tests run: `npm run build:sdk`. Tests import from `packages/sdk/dist/`, not from `src/`.

## No Root Imports

`packages/sdk/` must not import from the repo root `src/` — the SDK is a standalone package. Only import from `@relaycast/sdk` and `@agent-relay/config` as peer dependencies.

## README Maintenance

Before working here, read `packages/sdk/README.md`. After work, update Learnings with API behavior or protocol edge cases discovered.

Maintains: `packages/sdk/README.md`, `packages/sdk/src/workflows/README.md`

**Evidence:** `vitest.config.ts`, `packages/sdk/src/index.ts`, `package.json` (scripts.test:integration:broker)
