# Archeia

**Archeia is a standard and a kernel for agentic development: a minimal, in-repo substrate for structured project memory that AI agents read, write, and coordinate through — without a server, a schema registry, or a message broker between them.**

## The problem

AI coding agents don't fail because they can't reason. They fail because they can't find what's true, can't remember what was decided, and can't trust what they read. Context is the bottleneck, not intelligence.

Project knowledge today is scattered across a dozen tools an agent can't see: architecture lives in a senior dev's head, product decisions in Notion, roadmap in Linear, business vision in a pitch deck, growth experiments in a spreadsheet, task state in Jira, and the half that matters is a Slack thread from last March. Every agent session starts from zero and reconstructs context from file names and guesses.

Archeia closes that gap by putting the project's mind inside the project's repo.

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

Five claims, each of them either novel or stated as a first-class principle for the first time:

1. **Context is the bottleneck, not intelligence.** Structure is the cheapest intelligence multiplier available.
2. **The filesystem is already the database.** Directories, paths, markdown, and git already do what you were about to spin up a vector DB for.
3. **Ownership is the only concurrency primitive agents need.** Assign each domain to one writer family, and conflicts literally cannot happen.
4. **Project knowledge has a temporal state: past, present, future.** Every artifact refers to a moment, and that moment is a first-class field — not an afterthought.
5. **Agents compose via files, not APIs.** The filesystem is the message bus; frontmatter is the schema. Any agent framework in any language can participate.

Claim #4 is the one I have not seen anywhere else. Every other in-repo knowledge system (ADR, arc42, Diataxis, Docs as Code) is flat and present-tense. Archeia says: every artifact has a `temporal_state`, transitions between states are kernel operations, and history isn't an afterthought — it's the past half of the model.

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
