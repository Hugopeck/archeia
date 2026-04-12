# src

TypeScript CLI entry point and Rust broker binary for Agent Relay. This directory contains two parallel codebases that ship together: the TypeScript CLI (commands, hooks, adapters) and the Rust binary that implements the WebSocket relay broker.

## Structure

```mermaid
graph LR
    CLI[cli/index.ts] -->|parses commands| BOOT[cli/bootstrap.ts]
    BOOT -->|dispatches| CMD[cli/commands/]
    CMD -->|core/up/down/start| BLC[cli/lib/broker-lifecycle.ts]
    CMD -->|agent spawn/send| CF[cli/lib/client-factory.ts]
    CF -->|creates| SDK[@agent-relay/sdk]
    INDEX[index.ts] -->|re-exports| SDK
    INDEX -->|re-exports| MEM[memory/index.ts]
    MAIN[main.rs] -->|spawns agents| SPAWN[spawner.rs]
    MAIN -->|routes messages| ROUTE[routing.rs]
    MAIN -->|PTY I/O| PTY[pty_worker.rs]
    MAIN -->|cloud relay| WS[relaycast_ws.rs]
```

## Key Concepts

- **Dual runtime** — `src/cli/` is TypeScript (Node.js CLI); `src/main.rs` and `src/*.rs` is Rust (the broker binary that does the actual PTY management and WebSocket relay).
- **CLI commands** — `cli/commands/` contains 9 command groups: `core` (up/down/start/status), `setup`, `cloud`, `agent-management`, `messaging`, `monitoring`, `auth`, `doctor`, `swarm`. Each has a paired `.test.ts`.
- **Broker binary modules** — `spawner.rs` spawns CLI agents as PTY processes; `routing.rs` routes messages by agent name/channel; `pty_worker.rs` handles terminal I/O and prompt detection; `relaycast_ws.rs` manages the WebSocket connection to Relaycast Cloud.
- **TypeScript re-exports** — `src/index.ts` re-exports from `@agent-relay/sdk`, `src/utils/`, `src/hooks/`, and `src/memory/` so the npm package exposes a unified API.

## Usage

The CLI is the primary consumer of this directory. Users invoke `agent-relay up`, `agent-relay start`, etc., which are wired in `cli/commands/core.ts`. The Rust broker is spawned as a subprocess by `packages/sdk/src/client.ts` — it is not invoked directly by end users.

The TypeScript exports (`src/index.ts`) are consumed by downstream packages that import from the root `agent-relay` package.

**Evidence:** `src/cli/index.ts`, `src/cli/commands/core.ts`, `src/main.rs`, `src/index.ts`

## Learnings

_Seed entry — append learnings from work done here._
