# Personal Subagents

This folder contains [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) — role-shaped AI assistants that the main session can delegate work to. They coexist with the domain skills under `skills/`: skills own *workflows*, agents own *roles*.

## Install target

`install.sh` (at the repo root) symlinks every `agents/*.md` (except this README) into `~/.claude/agents/`, which is Claude Code's **user-level** subagent location. Once installed, the agents are available in every repo you open — not just archeia.

```bash
bash /Users/hugopeck/archeia/install.sh
ls -la ~/.claude/agents/
```

The symlinks point back into the repo, so a `git pull` on archeia immediately updates the installed agents — no re-install required.

## How they get invoked

Two ways, per the Claude Code docs:

1. **Automatic delegation** — when the main session encounters work whose shape matches an agent's `description` field, it delegates to that agent. The agent runs in its own context window, does the work, and returns a summary.
2. **Explicit** — `Task({ subagent_type: "architect", ... })` from the main thread, or `claude --agent architect` to run an entire session as that agent.

Subagents receive only their own system prompt (plus basic environment details) — not the parent's context. Use them when a side task would otherwise flood the main conversation with file reads or search output you won't reference again.

## Archeia awareness

Each agent in this folder names the exact `.archeia/<domain>/` paths it reads and writes, per the [Archeia Standard](../standard/SCHEMA.md). This is deliberate — agents are meant to coordinate with the domain skills (`archeia:write-tech-docs`, `archeia:review-draft`, `archeia:work`) by reading the same `.archeia/` tree, not by inventing parallel state.

**Still works in non-archeia repos.** When `.archeia/` doesn't exist in the target repo, each agent's "read this from `.archeia/...`" steps no-op and the agent falls back to generic code-reading behavior. You don't need the archeia monorepo cloned to use them.

## Current roster

| Agent | Role | Reads | Writes |
|---|---|---|---|
| [`architect.md`](architect.md) | System architecture, feasibility, ADR authoring | `.archeia/codebase/architecture/**`, `.archeia/product/product.md`, `.archeia/business/drafts/*.md` | `.archeia/product/decisions/*.md` |
| [`engineer.md`](engineer.md) | Implementation — task spec → working code | `.archeia/execution/tasks/<active>.md`, `.archeia/product/product.md`, `.archeia/codebase/standards/standards.md`, `.archeia/codebase/guide.md` | Source files, tests, task frontmatter updates |

This is a deliberately minimal starter set. Add your own (`designer`, `pm`, `qa`, `researcher`, etc.) by dropping a new `<role>.md` file here and re-running `install.sh`.

## Scope precedence (read this before adding project overrides)

Claude Code resolves subagents in precedence order:

1. `.claude/agents/` inside the current project (highest)
2. `~/.claude/agents/` (user-level — what this folder installs to)
3. Plugin-provided agents

If you drop a project-level `.claude/agents/architect.md` somewhere, it will override the user-level `architect` for that project only. This is usually what you want when one project needs a tweaked version — keep the base in archeia, override locally.

## Adding a new agent

1. Create `agents/<role>.md` in this folder.
2. Frontmatter must have `name: <role>` (matching filename) and a `description:` beginning with trigger phrases (`Use when...`).
3. Body is the agent's full system prompt. Keep it concrete — reference real `.archeia/` paths and the existing `archeia:<skill>` peers.
4. Re-run `install.sh` — the symlink lands in `~/.claude/agents/` and the agent is immediately available.

See `architect.md` and `engineer.md` for the canonical file shape.

## Reference

- Claude Code subagent docs: https://code.claude.com/docs/en/sub-agents
- Archeia Standard (defines the `.archeia/<domain>/` paths the agents read): [`../standard/SCHEMA.md`](../standard/SCHEMA.md)
