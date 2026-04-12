<!-- PRPM_MANIFEST_START -->

<skills_system priority="1">
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills (loaded into main context):

- Use the <path> from the skill entry below
- Invoke: Bash("cat <path>")
- The skill content will load into your current context
- Example: Bash("cat .openskills/backend-architect/SKILL.md")

Usage notes:

- Skills share your context window
- Do not invoke a skill that is already loaded in your context
  </usage>

<available_skills>

<skill activation="lazy">
<name>frontend-design</name>
<description>Design and build modern frontend interfaces with best practices and user experience principles. Create beautiful, accessible, and performant web interfaces.</description>
<path>.openskills/frontend-design/SKILL.md</path>
</skill>

</available_skills>
</skills_system>

<!-- PRPM_MANIFEST_END -->

# Git Workflow Rules

## NEVER Push Directly to Main

**CRITICAL: Agents must NEVER push directly to the main branch.**

- Always work on a feature branch
- Commit and push to the feature branch only
- Let the user decide when to merge to main
- Do not merge to main without explicit user approval

```bash
# CORRECT workflow
git checkout -b feature/my-feature
# ... do work ...
git add .
git commit -m "My changes"
git push origin feature/my-feature
# STOP HERE - let user merge

# WRONG - never do this
git checkout main
git merge feature/my-feature
git push origin main  # NO!
```

This ensures the user maintains control over what goes into the main branch.

<!-- prpm:snippet:start @agent-workforce/trail-snippet@1.0.1 -->

# Trail

Record your work as a trajectory for future agents and humans to follow.

## Usage

If `trail` is installed globally, run commands directly:

```bash
trail start "Task description"
```

If not globally installed, use npx to run from local installation:

```bash
npx trail start "Task description"
```

## When Starting Work

Start a trajectory when beginning a task:

```bash
trail start "Implement user authentication"
```

With external task reference:

```bash
trail start "Fix login bug" --task "ENG-123"
```

## Recording Decisions

Record key decisions as you work:

```bash
trail decision "Chose JWT over sessions" \
  --reasoning "Stateless scaling requirements"
```

For minor decisions, reasoning is optional:

```bash
trail decision "Used existing auth middleware"
```

**Record decisions when you:**

- Choose between alternatives
- Make architectural trade-offs
- Decide on an approach after investigation

## Completing Work

When done, complete with a retrospective:

```bash
trail complete --summary "Added JWT auth with refresh tokens" --confidence 0.85
```

**Confidence levels:**

- 0.9+ : High confidence, well-tested
- 0.7-0.9 : Good confidence, standard implementation
- 0.5-0.7 : Some uncertainty, edge cases possible
- <0.5 : Significant uncertainty, needs review

## Abandoning Work

If you need to stop without completing:

```bash
trail abandon --reason "Blocked by missing API credentials"
```

## Checking Status

View current trajectory:

```bash
trail status
```

## Why Trail?

Your trajectory helps others understand:

- **What** you built (commits show this)
- **Why** you built it this way (trajectory shows this)
- **What alternatives** you considered
- **What challenges** you faced

Future agents can query past trajectories to learn from your decisions.

<!-- prpm:snippet:end @agent-workforce/trail-snippet@1.0.1 -->

<!-- prpm:snippet:start @agent-relay/agent-relay-snippet@1.2.0 -->

# Agent Relay

Real-time agent-to-agent messaging via MCP tools.

## MCP Tools

All agent communication uses MCP tools provided by the Relaycast MCP server:

| Tool                           | Description                           |
| ------------------------------ | ------------------------------------- |
| `relay_send(to, message)`      | Send a message to an agent or channel |
| `relay_inbox()`                | Check your inbox for new messages     |
| `relay_who()`                  | List online agents                    |
| `relay_spawn(name, cli, task)` | Spawn a new worker agent              |
| `relay_release(name)`          | Release/stop a worker agent           |
| `relay_status()`               | Check relay connection status         |

## Sending Messages

```
relay_send(to: "AgentName", message: "Your message here")
```

| TO Value    | Behavior         |
| ----------- | ---------------- |
| `AgentName` | Direct message   |
| `*`         | Broadcast to all |
| `#channel`  | Channel message  |

## Spawning & Releasing

```
relay_spawn(name: "WorkerName", cli: "claude", task: "Task description")
relay_release(name: "WorkerName")
```

## Receiving Messages

Messages appear as:

```
Relay message from Alice [abc123]: Content here
```

Channel messages include `[#channel]`:

```
Relay message from Alice [abc123] [#general]: Hello!
```

## Protocol

- **ACK** when you receive a task: `ACK: Brief description`
- **DONE** when complete: `DONE: What was accomplished`
- Send status to your **lead**, not broadcast
<!-- prpm:snippet:end @agent-relay/agent-relay-snippet@1.2.0 -->

---
<!-- archeia:generated -->

## Architecture Reference

> Generated by archeia-write-tech-docs. Full docs in `.archeia/`.

Agent Relay is a TypeScript + Rust monorepo for real-time agent-to-agent communication. It ships as an npm package with a statically-linked Rust broker binary (`agent-relay-broker`), a TypeScript SDK (`@agent-relay/sdk`), and a Python SDK (`agent-relay-sdk`). Agents (Claude, Codex, Gemini) are spawned as PTY subprocesses by the Rust broker and communicate via Relaycast Cloud over WebSocket.

**Evidence:** `package.json`, `Cargo.toml`, `README.md`

### Tech Stack

- **Language:** TypeScript 5.x (primary), Rust 2021 (broker binary), Python (SDK)
- **Runtime:** Node.js ≥18.0.0; npm 10.5.1
- **Key deps:** express, ws, @relaycast/sdk, zod, posthog-node (TS); axum, tokio, relaycast (Rust)
- **Build:** turbo (workspace packages), tsc (root TS), cargo (Rust broker)
- **Tests:** vitest 3.x (unit); Node.js native test runner (SDK integration)

**Evidence:** `package.json`, `Cargo.toml`, `tsconfig.json`

### Setup and Dev Commands

```bash
npm install              # install deps + postinstall (binary setup)
npm run build            # full build: clean → Rust binary → turbo packages → tsc
npm run dev              # start relay on port 3888
npm run test             # vitest run (unit tests)
npm run test:integration # integration test suite
npm run lint             # ESLint (src/ TypeScript)
npm run format           # Prettier (all files)
npm run codegen:models   # regenerate cli-registry.generated.ts + models.py
```

**Evidence:** `package.json` (scripts)

### Project Structure

```
src/            TypeScript CLI + broker wrapper
src/main.rs     Rust broker (spawner, PTY, routing, WebSocket)
packages/       15 npm workspace packages (sdk, openclaw, config, memory, hooks, ...)
tests/          Integration, benchmark, parity, workflow tests
openclaw-web/   Next.js dashboard (SST/AWS)
```

Key boundary rules:
- `packages/sdk/` uses Node.js test runner, NOT vitest — do not add vitest tests there
- `packages/config/` contains codegen'd files — regenerate with `npm run codegen:models` after editing `packages/shared/cli-registry.yaml`

**Evidence:** `package.json` (workspaces), `vitest.config.ts`, `tsconfig.json`

### Coding Standards

- **Files:** kebab-case (e.g., `spawn-from-env.ts`)
- **Variables/functions:** camelCase; types/classes: PascalCase (ESLint enforced)
- **Unused vars:** prefix with `_` to suppress warnings
- **`any`:** permitted but discouraged (`no-explicit-any` is off)
- **Formatter:** Prettier — run `npm run format` (pre-commit hooks enforce this)
- **Linter:** ESLint — run `npm run lint`
- **TypeScript:** strict mode; all code must compile cleanly under `tsc`
- **Error handling:** no shared TS wrapper — match the nearest module's pattern

**Evidence:** `.eslintrc.cjs`, `.prettierrc`, `tsconfig.json`

### Full Documentation

- Architecture: `.archeia/codebase/architecture/architecture.md`
- Standards: `.archeia/codebase/standards/standards.md`
- Guide: `.archeia/codebase/guide.md`
- System context: `.archeia/codebase/architecture/system.json`
- Containers: `.archeia/codebase/architecture/containers.json`
- Data flow: `.archeia/codebase/architecture/dataflow.json`
