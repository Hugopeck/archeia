# Architecture

## Documentation Confidence

| Section | Confidence | Reason |
|---------|------------|--------|
| System Overview | high | Manifest and README clearly identify the system from `package.json`, `README.md` |
| Topology | high | Monorepo with workspaces in `package.json`, Rust binary in `Cargo.toml`, `fly.toml` for deployment |
| Module Boundaries | high | 15 workspace packages under `packages/`, each with their own `package.json` and `src/` |
| Data Flow | medium | Primary SDK→broker flow traced from `src/cli/bootstrap.js` and `packages/sdk/src/client.ts`; internal broker routing inferred |
| Build and Development | high | All commands in `package.json` scripts; Rust build via cargo |

**Overall: medium** (1 medium, 4 high)

**Low-confidence guidance:**
- **Data Flow:** Internal broker message routing is in the Rust binary (`src/main.rs`). Read `src/main.rs` routing module before modifying message-passing behavior.

## System Overview

Agent Relay is a TypeScript and Rust system for real-time agent-to-agent communication. It enables AI agents (Claude, Codex, Gemini) to spawn, communicate, and coordinate via a central broker. The system ships as an npm package (`agent-relay`) with a Rust binary broker (`agent-relay-broker`) and a Python SDK (`agent-relay-sdk`).

**Evidence:** `package.json`, `Cargo.toml`, `README.md`

## Topology

- **Type:** Monorepo — 15 npm workspace packages under `packages/`, 1 Rust binary, 1 Next.js web app (`openclaw-web`). Deployed as a cloud service on Fly.io.
- **Primary areas:**
  - `src/` — TypeScript CLI entry point and broker wrapper (builds to `dist/src/cli/index.js`)
  - `src/main.rs` — Rust binary broker implementing WebSocket relay, PTY spawning, and multi-workspace routing
  - `packages/sdk/` — TypeScript SDK (`@agent-relay/sdk`) consumed by end users
  - `packages/openclaw/` — OpenClaw gateway for receiving inbound messages from external platforms
  - `packages/config/` — Shared config models and CLI registry (includes codegen'd types from `packages/shared/cli-registry.yaml`)
  - `packages/memory/` — Memory adapters (in-memory, Supermemory) and context compaction
  - `packages/hooks/` — Lifecycle hooks (inbox-check, custom hooks)
  - `packages/policy/` — Policy engine for agent behavior rules
  - `packages/trajectory/` — Trajectory recording and compaction
  - `packages/telemetry/` — PostHog telemetry client
  - `packages/utils/` — Shared utilities
  - `packages/user-directory/` — User directory service
  - `packages/acp-bridge/` — ACP (Agent Communication Protocol) bridge
  - `openclaw-web/` — Next.js web dashboard (deployed via SST to AWS)
  - `tests/` — Integration, benchmarks, parity, and workflow tests
- **External systems:**
  - Relaycast cloud (via `@relaycast/sdk` in `package.json`, `relaycast` crate in `Cargo.toml`) — WebSocket relay backbone
  - PostgreSQL (via `pg` in `package.json`, `DATABASE_URL` in `.env.example`) — cloud mode persistence
  - PostHog (via `posthog-node` in `package.json`) — telemetry
  - Fly.io (via `fly.toml`) — cloud deployment
  - SQLite (via `AGENT_RELAY_STORAGE_TYPE=sqlite` in `.env.example`) — local mode persistence

**Evidence:** `package.json`, `Cargo.toml`, `fly.toml`, `.env.example`, `tsconfig.json`

## Module Boundaries

<!-- INSUFFICIENT EVIDENCE: internal source modules for Components.json -->

| Module | Path | Responsibility | Dependencies |
|--------|------|----------------|-------------|
| CLI / Broker wrapper | `src/` | TypeScript CLI entrypoint; wraps Rust broker binary | `@agent-relay/sdk`, `@agent-relay/config`, `@agent-relay/hooks` |
| Rust Broker | `src/main.rs`, `src/lib.rs` | WebSocket relay, PTY spawning, agent routing, multi-workspace | `relaycast`, `axum`, `tokio` |
| SDK | `packages/sdk/` | TypeScript client library for spawning agents and sending messages | `@relaycast/sdk`, `@agent-relay/config` |
| OpenClaw | `packages/openclaw/` | Inbound gateway for external messaging platforms; spawns agents | `@agent-relay/sdk`, `@relaycast/sdk` |
| Config | `packages/config/` | Shared config types, relay file writer, CLI registry | none |
| Memory | `packages/memory/` | Memory adapters and context compaction | `@agent-relay/utils` |
| Hooks | `packages/hooks/` | Inbox-check and lifecycle hooks | `@agent-relay/config` |
| Policy | `packages/policy/` | Agent policy engine | `@agent-relay/config` |
| Trajectory | `packages/trajectory/` | Trajectory recording for agent sessions | `@agent-relay/config` |
| Telemetry | `packages/telemetry/` | PostHog event tracking | `posthog-node` |
| Utils | `packages/utils/` | Shared utility functions | none |
| User Directory | `packages/user-directory/` | User identity lookup | `@agent-relay/config` |
| ACP Bridge | `packages/acp-bridge/` | ACP protocol bridge | `@agent-relay/sdk` |
| SDK (Python) | `packages/sdk-py/` | Python client SDK (`agent-relay-sdk` on PyPI) | none |
| OpenClaw Web | `openclaw-web/` | Next.js dashboard for managing OpenClaw workspaces | SST |

**Evidence:** `package.json` (workspaces, bundledDependencies), `tsconfig.json` (paths aliases), `packages/openclaw/src/index.ts`, `packages/sdk/src/index.ts`, `src/index.ts`

## Data Flow

Primary use case: orchestrating a multi-agent conversation via the TypeScript SDK.

| Step | Source | Target | Message | Type | Protocol | Evidence |
|------|--------|--------|---------|------|----------|----------|
| 1 | Developer | SDK (`AgentRelay`) | `new AgentRelay()` + connect | sync | function call | `packages/sdk/src/client.ts` |
| 2 | SDK | Rust Broker | Spawn broker subprocess | sync | IPC (subprocess) | `packages/sdk/src/client.ts` |
| 3 | SDK | Relaycast Cloud | WebSocket connect | sync | WebSocket | `packages/sdk/src/client.ts`, `Cargo.toml` (`relaycast`) |
| 4 | SDK | Rust Broker | `relay.claude.spawn({...})` | sync | function call | `packages/sdk/src/client.ts`, `README.md` |
| 5 | Rust Broker | Claude CLI | Spawn PTY process | async | PTY | `src/main.rs` (`spawner` module) |
| 6 | Claude Agent | Rust Broker | Send message via relay MCP | async | WebSocket | `src/main.rs` (`routing` module) |
| 7 | Rust Broker | Relaycast Cloud | Broadcast message | async | WebSocket | `src/main.rs` (`relaycast_ws` module) |
| 8 | Relaycast Cloud | Rust Broker | Deliver to target agent | async | WebSocket | `Cargo.toml` (`relaycast` dep) |
| 9 | Rust Broker | Target Agent | Inject message into PTY | async | PTY | `src/main.rs` (`pty_worker` module) |
| 10 | SDK | Developer | `onMessageReceived` callback | response | function call | `README.md`, `packages/sdk/src/client.ts` |

**Evidence:** `packages/sdk/src/client.ts`, `src/main.rs`, `README.md`, `Cargo.toml`

## Build and Development

- **Package manager:** npm (`package-lock.json` + `prpm.lock` present)
- **Build command:** `npm run build` (cleans, builds Rust broker, builds workspace packages via turbo, then runs `tsc`)
- **Dev command:** `npm run dev` (runs `node dist/src/cli/index.js up --port 3888`)
- **Test runner:** vitest (`vitest.config.ts`), with integration tests via `node tests/integration/run-all-tests.js`
- **Task automation:** turbo (`turbo.json`) for workspace builds; husky pre-commit hooks (`.husky/pre-commit`)

**Evidence:** `package.json` (scripts), `vitest.config.ts`, `turbo.json`, `.husky/pre-commit`

## Deployment

Agent Relay deploys to Fly.io as a single Express app (`fly.toml`). The Rust broker binary is built separately via CI (`build-broker-binary.yml`) as a static musl binary for Linux x86_64 and aarch64. The OpenClaw web dashboard deploys separately via SST (`package.json` script `dev:web`).

- **Cloud target:** Fly.io (`app = "agent-relay"`, `primary_region = "sjc"`)
- **Container:** rolling deployment strategy, 1 machine minimum, 512 MB RAM
- **Health check:** `GET /health` on port 3000 every 30s
- **Broker binaries:** built by `.github/workflows/build-broker-binary.yml` and uploaded as GitHub release artifacts

**Evidence:** `fly.toml`, `.github/workflows/build-broker-binary.yml`

## API Surface

The CLI exposes `agent-relay` binary commands (from `package.json` bin field). The SDK exposes:
- `AgentRelay` class — connect, spawn agents, send messages, shutdown
- `relay.claude.spawn()`, `relay.codex.spawn()` — spawn CLI-based agents
- `relay.system().sendMessage()` — send messages to named agents
- `relay.waitForAgentReady()`, `AgentRelay.waitForAny()` — wait for agent events

The OpenClaw gateway exposes `InboundGateway` for receiving messages from external platforms (Relaycast events).

The `openapi.yaml` file documents additional HTTP API endpoints.

**Evidence:** `packages/sdk/src/index.ts`, `packages/sdk/src/client.ts`, `packages/openclaw/src/index.ts`, `openapi.yaml`, `README.md`
