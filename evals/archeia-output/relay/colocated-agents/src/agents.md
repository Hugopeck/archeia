# agents.md — src/

## Language Boundary

This directory contains TypeScript (`src/cli/`, `src/hooks/`, `src/*.ts`) and Rust (`src/*.rs`, `src/cli.rs` sibling modules). They are separate runtimes that ship together. Do not mix TypeScript patterns into `.rs` files or vice versa.

## Rust Broker Rules

- Rust entry point: `src/main.rs`; library: `src/lib.rs`. All broker logic is in these files and their sibling modules (`spawner.rs`, `routing.rs`, `pty_worker.rs`, `relaycast_ws.rs`, etc.).
- Build with `npm run build:rust` (invokes cargo release build). Do not run `cargo build` manually without the wrapper — the wrapper copies the binary to `packages/sdk/bin/`.
- Logging in Rust uses `tracing` crate only. Do not `println!` in production paths.

## TypeScript CLI Rules

- `src/cli/index.ts` has an `isEntrypoint()` guard — the file can be imported without running the CLI. Do not remove this guard.
- CLI commands never invoke the Rust broker directly — they go through `@agent-relay/sdk`.
- Do not add vitest tests in `src/` for anything that requires a running broker — those belong in `tests/integration/`.

## Testing

- Unit tests: `src/**/*.test.ts` — run via vitest (`npm test`).
- Tests that require a live broker go in `tests/integration/` or `tests/parity/`, not here.

## README Maintenance

Before working in this directory or its children, read `src/README.md` and `src/cli/README.md`. After completing work, update the relevant README's Learnings section with anything non-obvious.

Maintains: `src/README.md`, `src/cli/README.md`

**Evidence:** `src/cli/index.ts`, `src/main.rs`, `Cargo.toml`, `package.json` (scripts.build:rust), `vitest.config.ts`
