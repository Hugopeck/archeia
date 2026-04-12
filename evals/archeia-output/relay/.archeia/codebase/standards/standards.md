# Standards

## Documentation Confidence

| Section | Confidence | Reason |
|---------|------------|--------|
| Language and Runtime | high | TypeScript 5.x and Node.js ≥18 from `package.json`, `tsconfig.json`, `.nvmrc` |
| Formatting and Linting | high | Prettier configured (`.prettierrc`), ESLint configured (`.eslintrc.cjs`) |
| Typing and Static Analysis | high | TypeScript strict mode in `tsconfig.json` |
| Project Structure | high | Clear monorepo layout with `packages/`, `src/`, `tests/` |
| Naming Conventions | high | ESLint `naming-convention` rule enforces camelCase variables, PascalCase types; kebab-case files |
| Testing | high | vitest configured (`vitest.config.ts`); Node.js test runner for SDK integration tests |
| Error Handling and Logging | medium | No structured error pattern detected in sampled files; tracing/subscriber in Rust (`Cargo.toml`) |

**Overall: medium** (1 medium, 6 high)

**Low-confidence guidance:**
- **Error Handling and Logging:** No shared error-handling wrapper detected in TypeScript code. Follow the pattern of the nearest module. The Rust broker uses `tracing` crate for structured logging.

## Language and Runtime

- **Languages:** TypeScript (primary), Rust (broker binary), Python (SDK)
- **TypeScript version:** ^5.9.3 (from `package.json` devDependencies)
- **Runtime:** Node.js ≥18.0.0 (from `package.json` engines field)
- **Rust edition:** 2021 (from `Cargo.toml`)
- **Package manager:** npm 10.5.1 (`package-lock.json` present; `prpm.lock` also present for workspace dependency management)
- **Entry points:**
  - `dist/src/cli/index.js` — `agent-relay` CLI binary
  - `dist/src/index.js` — main library export
  - `src/main.rs` — Rust broker binary
  - `packages/sdk-py/agent_relay/` — Python SDK package

**Evidence:** `package.json` (engines, packageManager, bin, main), `Cargo.toml`, `tsconfig.json`, `.nvmrc`

## Formatting and Linting

**Formatter:** Prettier 3.x (`.prettierrc`)
- Run: `npm run format` (from `package.json` scripts.format)
- Check: `npm run format:check`
- Applies to: `*.{ts,tsx,json,md,mdx,yml,yaml}` (from `package.json` lint-staged)

**Linter:** ESLint 8.x with `@typescript-eslint` plugin (`.eslintrc.cjs`)
- Run: `npm run lint` (runs `eslint src --ext .ts`)
- Notable rules:
  - `no-explicit-any`: off (intentionally disabled for early release)
  - `no-unused-vars`: warn (args/vars prefixed with `_` are exempt)
  - `naming-convention`: warn (camelCase/UPPER_CASE/PascalCase variables; PascalCase types)
  - `complexity`: warn at 15
  - `max-depth`: warn at 4
- Pre-commit: lint-staged runs ESLint fix + Prettier on staged files (`.husky/pre-commit`)

**Evidence:** `.prettierrc`, `.eslintrc.cjs`, `package.json` (scripts, lint-staged), `.husky/pre-commit`

## Typing and Static Analysis

- **Type checker:** TypeScript strict mode (`"strict": true` in `tsconfig.json`)
- **Target:** ES2022, NodeNext module system
- **Declaration files:** generated (`"declaration": true`, `"declarationMap": true`)
- **Source maps:** enabled (`"sourceMap": true`)
- **Path aliases:** workspace packages resolved via `tsconfig.json` paths (e.g., `@agent-relay/config` → `packages/config/dist/`)
- **skipLibCheck:** true (from `tsconfig.json`)

**Evidence:** `tsconfig.json`

## Project Structure

```
relay/
├── src/               TypeScript CLI and broker wrapper
│   ├── cli/           Command implementations and CLI bootstrap
│   ├── main.rs        Rust broker binary entry point
│   └── lib.rs         Rust broker library
├── packages/          npm workspace packages (15 packages)
│   ├── sdk/           TypeScript SDK for end users
│   ├── openclaw/      OpenClaw gateway
│   ├── config/        Shared config types and codegen'd registry
│   ├── memory/        Memory adapters
│   ├── hooks/         Lifecycle hooks
│   └── ...
├── tests/             Integration, benchmark, parity, workflow tests
├── openclaw-web/      Next.js web dashboard
├── docs/              Documentation (Markdown and reference)
├── scripts/           Build, codegen, and dev utility scripts
└── examples/          Example multi-agent programs
```

Workspace packages are bundled into the root npm package for distribution.

**Evidence:** `package.json` (workspaces, bundledDependencies), `tsconfig.json`, directory structure

## Naming Conventions

- **Files:** kebab-case for TypeScript source files (e.g., `error-handler.ts`, `spawn-from-env.ts`)
- **Variables/functions:** camelCase (enforced by ESLint `naming-convention` rule)
- **Types/interfaces/classes:** PascalCase (enforced by ESLint `naming-convention` rule)
- **Constants:** UPPER_CASE permitted (ESLint `naming-convention` rule)
- **Unused identifiers:** prefix with `_` to suppress unused-vars warnings
- **Rust:** standard Rust conventions (snake_case functions/modules, PascalCase structs/enums)

**Evidence:** `.eslintrc.cjs` (naming-convention rule), source file inspection (`packages/sdk/src/`)

## Testing

- **Unit test framework:** vitest 3.x (`vitest.config.ts`)
  - Test files: `src/**/*.test.ts`, `packages/**/src/**/*.test.ts`
  - Excludes: `packages/sdk/**` (uses Node.js test runner instead)
  - Coverage thresholds: lines 60%, functions 60%, branches 50%, statements 60%
  - Coverage provider: v8
  - Environment: node
- **SDK integration tests:** Node.js native test runner (`node --test`)
  - Location: `tests/integration/broker/`
  - Run: `npm run test:integration:broker`
- **Full integration tests:** `npm run test:integration` (runs `tests/integration/run-all-tests.js`)
- **Run all vitest tests:** `npm test` (calls `vitest run`)
- **Coverage:** `npm run test:coverage`
- **Test setup:** `test/vitest.setup.ts`

**Evidence:** `vitest.config.ts`, `package.json` (scripts.test, scripts.test:integration, scripts.test:coverage)

## Error Handling and Logging

<!-- INSUFFICIENT EVIDENCE: No shared TypeScript error-handling pattern detected in sampled source files -->

- **Rust broker:** uses `tracing` crate (0.1) and `tracing-subscriber` with env-filter for structured logging (`Cargo.toml`)
- **TypeScript:** no shared wrapper detected; `anyhow` equivalent not present in TS deps

**Evidence:** `Cargo.toml` (tracing, tracing-subscriber)
