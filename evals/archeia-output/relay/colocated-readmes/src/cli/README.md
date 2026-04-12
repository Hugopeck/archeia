# src/cli

CLI bootstrap and command implementations for the `agent-relay` binary. Parses arguments via Commander, dispatches to command modules, and uses a shared library for broker lifecycle, client creation, and output formatting.

## Structure

```mermaid
graph LR
    ENTRY[index.ts] -->|isEntrypoint check| BOOT[bootstrap.ts]
    BOOT -->|registers commands| CMD[commands/]
    CMD -->|core: up/down/start/status/bridge| BLC[lib/broker-lifecycle.ts]
    CMD -->|spawn/release agents| CF[lib/client-factory.ts]
    CMD -->|messaging/monitoring| SDK[@agent-relay/sdk AgentRelayClient]
    CF --> SDK
    BLC --> SDK
    CMD -->|setup flow| CFG[@agent-relay/config]
    LIB[lib/index.ts] -->|formatting, paths, jsonc| CMD
```

## Key Concepts

- **Bootstrap guard** — `index.ts` calls `runCli()` only when it is the actual entrypoint (`isEntrypoint()` check), so the module can also be imported without triggering CLI execution.
- **Command groups** — `commands/core.ts` wires the lifecycle commands (`up`, `down`, `start`, `status`, `bridge`); `commands/agent-management.ts` handles spawn/release/list; `commands/messaging.ts` handles send/inbox; `commands/monitoring.ts` handles logs and events.
- **Client factory** — `lib/client-factory.ts` creates `AgentRelayClient` instances and provides `spawnAgentWithClient` for consistent agent spawning across commands.
- **No direct broker invocation** — CLI commands never call the Rust binary directly; they always go through `@agent-relay/sdk`'s `AgentRelayClient`.

## Usage

Imported by `src/cli/index.ts`. End users run `agent-relay <command>` via the npm `bin` entry. Other packages import specific utilities from `lib/index.ts`.

**Evidence:** `src/cli/index.ts`, `src/cli/bootstrap.ts`, `src/cli/commands/core.ts`, `src/cli/lib/index.ts`

## Local Development

```bash
npm run build          # build before running CLI
npm run dev            # run relay on port 3888
node dist/src/cli/index.js <command>   # invoke directly after build
```

**Evidence:** `package.json` (scripts.build, scripts.dev)

## Learnings

_Seed entry — append learnings from work done here._
