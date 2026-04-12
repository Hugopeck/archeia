# Archeia

**Archeia is a standard and a kernel for agentic development: a minimal, in-repo substrate for structured project memory that AI agents read, write, and coordinate through — without a server, a schema registry, or a message broker between them.**

## The problem

AI coding agents don't fail because they can't reason. They fail for two reasons, and both of them are solvable by giving them a better surface to work on.

**The first bottleneck is context.** Agents can't find what's true, can't remember what was decided, and can't trust what they read. Project knowledge is scattered across a dozen tools an agent can't see: architecture lives in a senior dev's head, product decisions in Notion, roadmap in Linear, business vision in a pitch deck, growth experiments in a spreadsheet, task state in Jira, and the half that matters is a Slack thread from last March. Every agent session starts from zero and reconstructs context from file names and guesses.

**The second bottleneck is human-agent collaboration.** Humans need to direct, observe, intervene, hand off, recover, and audit — safely, recoverably, traceably, sync and async. A chat window can hold a conversation but it cannot hold a collaboration. Without a shared surface where both humans and agents can persist, edit, and audit work, every attempt to scale agentic work past a one-shot conversation collapses back into "type everything in the chat," which doesn't scale at all.

Archeia closes both gaps by putting the project's mind inside the project's repo — a place where agents can find what they need *and* where humans and agents can work on the same artifacts at the same time, with git handling safety, recovery, traceability, and async coordination for free.

## What you get

A single directory, `.archeia/`, at the root of your project. Five canonical domains inside it:

- **`business/`** — why we're building, for whom, how we earn
- **`product/`** — what we've committed to build
- **`codebase/`** — what the code is, right now
- **`growth/`** — how we acquire, retain, monetize
- **`execution/`** — what we're doing right now

Every artifact inside has a **temporal state** — past, present, or future — in its frontmatter. Every domain has exactly one writer family. Every file is markdown with YAML frontmatter, readable by humans in any editor and parseable by agents in any framework.

That's the whole substrate. No server, no database, no API, no protocol layer. The filesystem is the database. Ownership is the concurrency model. YAML is the schema. Git is the audit log.

## What makes it new

Six claims, each of them either novel or stated as a first-class principle for the first time:

1. **Context is the bottleneck, not intelligence.** Structure is the cheapest intelligence multiplier available.
2. **Human-agent collaboration is the second bottleneck.** Without a shared surface where both humans and agents can work safely and recoverably, every collaboration collapses back into the chat window.
3. **The filesystem is already the database AND the canvas.** Directories, paths, markdown, and git already solve agent memory and human-agent coordination simultaneously. You don't need a memory service, and you don't need a project board.
4. **Ownership plus delegation is the concurrency model.** Each domain has one owner. When the owner needs parallelism, it delegates to subagents that return results; the owner integrates and commits. No concurrent writes, no locks, no CRDTs, no merge algorithms — just disciplined ownership and the subagent primitive.
5. **Project knowledge comes in three lifecycle shapes: living, accumulating, transient.** Most of `.archeia/` is living documents (one file per concept, edited in place, history in git). A smaller subset is accumulating records (ADRs, retros — append-only, never deleted). A minority is transient artifacts (tasks, drafts — flow through states with bounded retention, then pruned with git as the backstop). Each shape gets the minimum machinery it needs; nothing duplicates git.
6. **Agents compose via files, not APIs.** The filesystem is the message bus; frontmatter is the schema. Any agent framework in any language can participate.

Claims #2 and #5 are the ones I haven't seen anywhere else. Every other in-repo knowledge system (ADR, arc42, Diataxis, Docs as Code) is flat, present-tense, agent-blind, and lifecycle-naive. Archeia says: name both bottlenecks, give them a single shared substrate, recognize that different artifacts have fundamentally different lifecycles and match the machinery to each, and let subagent delegation do the concurrency work that locks and CRDTs try and fail to do elsewhere.

## What it replaces

Instead of a wiki + a ticket system + an ADR repo + a docs site + a memory service + a scattered set of specs spread across six tools, you have one canonical location in the repo where everything lives, versioned with the code, visible in every clone.

- Notion and Confluence are replaced by `.archeia/product/` and `.archeia/business/` for the parts agents need to read
- Jira and Linear are replaced by `.archeia/execution/` for task and project state
- ADR repos are replaced by `.archeia/product/decisions/`
- Architecture doc tools are replaced by `.archeia/codebase/architecture/`
- Agent memory services are replaced by the whole tree

You keep the tools that serve humans only. You move the tools that should have been serving agents.

## The dual structure: Standard + Distribution

**The Archeia Standard** is the formal, open specification. It defines the kernel — primitives, operations, invariants, schemas, contracts. It's what you cite when you're implementing or extending.

**Distributions** are opinionated bundles that extend the kernel for a specific audience. Each distribution picks its skills, its agents, its ethos, its workflow defaults. The standard itself is audience-neutral.

The reference distribution is **Archeia Solo**: a complete, unapologetically opinionated workspace for solo builders and one-person companies who direct AI agents to ship bootstrapped software products from day one. Archeia Solo ships 16 skills and a growing agent roster optimized for the ship-fast-charge-early loop.

Other distributions will come: Archeia Research for labs, Archeia Studio for game teams, Archeia Enterprise for compliance-heavy environments. They all share the same kernel.

## Who it's for

Anyone building software with AI agents and realizing the agents need a place to coordinate that isn't the chat window.

Solo builders especially: **Archeia Solo** is purpose-built for the one-person-plus-agents economy, where a single operator directs many agents to build and ship revenue-earning products without a team or runway. If that's you, start with Archeia Solo.

If you're building something else — a research pipeline, a game studio workflow, a compliance-heavy enterprise process — the kernel is what you extend. Write your own distribution.

## Start here

- **Read the kernel:** [`standard/SCHEMA.md`](../standard/SCHEMA.md) — the formal spec
- **Read the principles:** [`standard/PRINCIPLES.md`](../standard/PRINCIPLES.md) — the five fundamental truths
- **Read the temporal model:** [`standard/TEMPORAL_MODEL.md`](../standard/TEMPORAL_MODEL.md) — past, present, future and why it matters
- **Try Archeia Solo:** [`standard/distributions/solo-builder.md`](../standard/distributions/solo-builder.md) — the reference distribution, ready to install
- **Install:** `bash install.sh` drops the skills into `~/.claude/skills/` and the agents into `~/.claude/agents/`

Archeia is a way to give AI agents a shared memory and a way of working together. It's small enough to explain on one page and rigorous enough to implement as an open standard. The rest is skills, agents, and the discipline to write everything down where the agents can find it.
