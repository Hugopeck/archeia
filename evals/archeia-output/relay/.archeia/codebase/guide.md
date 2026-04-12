# Guide

## Prerequisites

- Node.js ≥18.0.0 (from `package.json` engines; `.nvmrc` present for nvm users)
- npm 10.5.1 (from `package.json` packageManager)
- Rust stable toolchain with cargo (for building the broker binary; optional if using prebuilt)
- Optional: musl-tools (Linux, for static binary builds via CI)

**Evidence:** `package.json` (engines, packageManager), `Cargo.toml`, `.nvmrc`, `.github/workflows/build-broker-binary.yml`

## Setup

1. Clone and install dependencies:
   ```bash
   npm install
   ```
   (from `package.json` postinstall — runs `scripts/postinstall.js` to set up binary)

2. Set up environment:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to configure storage type, ports, and cloud credentials as needed.

3. Build workspace packages and TypeScript:
   ```bash
   npm run build
   ```
   This cleans, builds the Rust broker binary (if cargo is installed), builds all workspace packages via turbo, and runs `tsc`.

4. Install git hooks:
   ```bash
   npm run hooks:install
   ```
   (from `package.json` scripts.hooks:install, runs `.scripts/hooks/install.sh`)

**Evidence:** `package.json` (scripts: postinstall, build, hooks:install), `.env.example`, `.husky/pre-commit`

## Local Development

Run the relay in development mode (builds first, then starts with hot reload):

```bash
npm run dev
```
Starts `node dist/src/cli/index.js up --port 3888` — relay listens on port 3888 by default.

Watch mode (TypeScript only, after initial build):
```bash
npm run dev:watch
```

Build and link globally for testing the CLI:
```bash
npm run dev:local
# Unlink:
npm run dev:unlink
```

Build the web dashboard (OpenClaw):
```bash
npm run dev:web
```
Starts the Next.js dashboard via SST (`openclaw-web/`).

**Evidence:** `package.json` (scripts: dev, dev:watch, dev:local, dev:unlink, dev:web)

## Testing

Run all vitest unit tests:
```bash
npm test
```
(calls `vitest run`; requires packages to be built first via pretest hook)

Run tests in watch mode:
```bash
npm run test:watch
```

Run tests with coverage:
```bash
npm run test:coverage
```
(coverage thresholds: lines 60%, functions 60%, branches 50%)

Run SDK integration tests (Node.js test runner):
```bash
npm run test:integration
```
or for broker-specific integration:
```bash
npm run test:integration:broker
```

**Evidence:** `package.json` (scripts: test, test:watch, test:coverage, test:integration), `vitest.config.ts`

## Common Tasks

| Task | Command | Source |
|------|---------|--------|
| Build everything | `npm run build` | `package.json` scripts.build |
| Build packages only (turbo) | `npm run build:packages` | `package.json` scripts.build:packages |
| Build Rust broker only | `npm run build:rust` | `package.json` scripts.build:rust |
| Build CJS bundle | `npm run build:cjs` | `package.json` scripts.build:cjs |
| Clean build artifacts | `npm run clean` | `package.json` scripts.clean |
| Lint TypeScript | `npm run lint` | `package.json` scripts.lint |
| Format code | `npm run format` | `package.json` scripts.format |
| Format check | `npm run format:check` | `package.json` scripts.format:check |
| Codegen shared models | `npm run codegen:models` | `package.json` scripts.codegen:models |
| Check CLI version sync | `npm run check:cli-versions` | `package.json` scripts.check:cli-versions |
| Update CLI versions | `npm run update:cli-versions` | `package.json` scripts.update:cli-versions |
| Dependency audit | `npm run audit:deps` | `package.json` scripts.audit:deps |
| Check unused exports | `npm run knip` | `package.json` scripts.knip |
| Check dep version sync | `npm run syncpack` | `package.json` scripts.syncpack |
| Scan TODOs | `npm run todo:scan` | `package.json` scripts.todo:scan |
| Serve docs locally | `npm run docs` | `package.json` scripts.docs |

**Evidence:** `package.json` (scripts section)

## Lint and Format

Lint TypeScript source:
```bash
npm run lint
```
(ESLint with `@typescript-eslint`, targets `src/` with `.ts` extension)

Format all files:
```bash
npm run format
```
(Prettier with `.prettierrc` config)

Check formatting without writing:
```bash
npm run format:check
```

Pre-commit hooks run both ESLint fix and Prettier automatically on staged files via husky + lint-staged.

**Evidence:** `package.json` (scripts: lint, format, format:check, lint-staged), `.eslintrc.cjs`, `.prettierrc`, `.husky/pre-commit`

## Deployment

Deploy to Fly.io (cloud API):
```bash
fly deploy
```
Configuration in `fly.toml` — rolling deploy strategy, min 1 machine, port 3000.

Build release broker binary (done via CI):
- GitHub Actions workflow: `.github/workflows/build-broker-binary.yml`
- Produces static musl binaries for Linux x86_64 and aarch64
- Uploaded as GitHub release artifacts

Deploy OpenClaw web dashboard (SST to AWS):
```bash
npm run dev:web
```
(SST config in `openclaw-web/`)

Publish npm package:
- See `.github/workflows/publish.yml`
- Requires `npm run build` first (via prepack hook)

**Evidence:** `fly.toml`, `.github/workflows/build-broker-binary.yml`, `.github/workflows/publish.yml`, `package.json` (scripts: prepack, dev:web)
