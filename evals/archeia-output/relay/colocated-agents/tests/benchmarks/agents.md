# agents.md — tests/benchmarks/

## Execution Model

Benchmarks are NOT vitest tests. Run them directly with tsx:
```bash
npx tsx tests/benchmarks/<name>.ts [--quick]
```
Do not add benchmark files to `vitest.config.ts` includes — they require a live broker binary and will fail in vitest.

## Binary Location

Benchmarks use `AGENT_RELAY_BIN` env var to locate the broker binary. If not set, `harness.ts` auto-detects from `target/debug/` or `target/release/`. Always set this explicitly in CI:
```bash
AGENT_RELAY_BIN=./target/release/agent-relay-broker npx tsx tests/benchmarks/throughput.ts
```

## `--quick` Flag

Pass `--quick` to reduce iteration counts and durations for fast validation. The `QUICK` constant in `harness.ts` gates this. All new benchmarks should honor this flag.

## Harness Dependency

All benchmarks must import `startBroker`, `resolveBinaryPath`, and `randomName` from `./harness.ts`. Do not copy-paste the broker startup logic — it has retry and timing handling that matters for benchmark accuracy.

## README Maintenance

Before working here, read `tests/benchmarks/README.md`. After work, update Learnings with anything non-obvious about timing, flakiness, or binary behavior.

Maintains: `tests/benchmarks/README.md`, `tests/parity/README.md`

**Evidence:** `tests/benchmarks/harness.ts`, `vitest.config.ts`
