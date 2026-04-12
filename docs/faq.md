# Archeia FAQ

Quick answers to questions someone reading Archeia for the first time will have. If you want the long-form pitch, read [the manifesto](manifesto.md) first. If you want the formal spec, read [the kernel](../standard/KERNEL.md).

---

## What is Archeia, in one sentence?

Archeia is an open standard and a minimal substrate for giving AI agents a shared, structured, in-repo memory so they can coordinate with each other and with humans without a server, a schema registry, or a message broker.

## Why does it exist?

Because AI coding agents don't fail for lack of intelligence — they fail because they can't find what's true, can't remember what was decided, and can't trust what they read. Project knowledge is scattered across a dozen tools agents can't see. And even when agents do have memory, humans and agents still need a shared surface to work on together: a place where both can persist, edit, audit, and recover work safely.

Archeia closes both gaps by putting the project's mind inside the project's repo, as structured markdown files that humans edit in their editor and agents edit via their tools.

## Who is it for?

Two audiences:

1. **Anyone building software with AI agents** who has hit the wall of "the agents need a place to coordinate that isn't the chat window." The Archeia Standard — the kernel plus the canonical software layout — is for you. You adopt it by organizing your repo's `.archeia/` directory per [`SCHEMA.md`](../standard/SCHEMA.md).

2. **Solo builders shipping bootstrapped software products with AI agents doing most of the work.** The reference distribution, [Archeia Solo](../standard/distributions/solo-builder.md), is built specifically for you. It makes all the configuration choices ahead of time, ships 16 opinionated skills, and refuses several framings (VC logic, team-later, PMF rituals) that would waste your time.

Future distributions will target research labs, game studios, enterprise teams, and open-source projects with monetization intent. They all share the same kernel.

---

## How is Archeia different from...

### ...a wiki (Notion, Confluence, Obsidian)?

Wikis live outside the repo. Agents can't see them without API keys, auth setup, or scraping. Wikis also have no lifecycle model — a one-year-old strategy doc sits next to a current one and nothing tells you which is which.

Archeia lives in the repo (versioned with the code, visible in every clone) and has an explicit lifecycle model (living documents evolve in place, accumulating records stay forever with status fields, transient artifacts get pruned after retention windows). Any agent with filesystem access can read and write Archeia. No auth setup.

**When a wiki is still right:** team-scale knowledge that deliberately should NOT be in the repo — HR material, customer-facing docs, proprietary research that shouldn't be public. Archeia is for project-scoped knowledge that agents need.

### ...a ticket system (Jira, Linear, GitHub Issues)?

Ticket systems are transient-artifact stores for operational work. They do one shape of artifact (the ticket) well, at the cost of:

- Living outside the repo (agents can't see them)
- Requiring API auth
- Having no model for living documents (product specs) or accumulating records (decisions)
- Imposing a workflow vocabulary that may not match the team's

Archeia Solo's `execution/` domain replaces the ticket-system-for-yourself use case — tasks, projects, plans, and retros all live in the repo as markdown files. The operator reads them in their editor; agents read them via tools; git preserves history.

**When a ticket system is still right:** customer-facing issue tracking, multi-team coordination across repos, or any case where non-developer stakeholders need a GUI to interact with the work.

### ...a vector database / memory service (Pinecone, Weaviate, Mem0)?

Vector DBs and memory services are the default answer to "give AI agents memory." They work. They're also dramatically over-engineered for the problem.

Agents don't usually need semantic search over their memory — they need to find the exact canonical spec, the exact locked decision, the exact current task. Paths and frontmatter beat embeddings for this. The directory `.archeia/product/product.md` is always the product spec. No retrieval query, no ranking, no relevance threshold, no hallucinated near-match.

Vector databases also have no native concept of ownership, lifecycle shape, or cross-domain contracts — the things Archeia makes central. You end up building those on top.

**When a vector DB is still right:** search over large unstructured corpora where you genuinely don't know where the answer is. For project-scoped knowledge with known structure, the filesystem wins.

### ...RAG (retrieval-augmented generation)?

RAG is a retrieval strategy, not a storage format. RAG over an unstructured pile of documents is weaker than direct path access to a structured tree. RAG over an Archeia tree is stronger than RAG over an unstructured pile.

The best answer is usually: give the agent the exact file it needs via path + frontmatter filter, fall back to glob + grep, fall back to RAG only if the previous two aren't enough. Most of the time they are.

Archeia is compatible with RAG — you can build a vector index over `.archeia/` and query it with a RAG pipeline. But most agents won't need to.

### ...a knowledge graph (RDF, property graphs, Neo4j)?

Knowledge graphs model typed relationships between entities. They're powerful for queries like "which components depend on which databases" or "which features require which permissions."

Archeia's `codebase/architecture/*.json` files encode a lightweight knowledge graph (the C4 model with typed relationships). You can load them into a formal graph database if you want to run Cypher queries. But most of the time, the agent reading them needs to answer one specific question ("is this architecture feasible for that draft feature?") and a structured JSON file with `evidence:` citations is enough.

Archeia is compatible with knowledge graph tooling but doesn't require it.

### ...docs as code (Docusaurus, MkDocs, arc42, Diataxis)?

Docs-as-code tools render static sites from markdown. Archeia uses markdown for the same reason — human-readable, agent-parseable, git-native. But:

- Docs-as-code tools optimize for human-reader rendering (search, navigation, beautiful HTML).
- Archeia optimizes for agent-writer and multi-shape lifecycle.

They're compatible. You can point MkDocs at `.archeia/` and get a rendered docs site. But Archeia's primary consumer is the agent reading the raw files, not the human browsing a rendered site. The rendering layer is optional, not central.

### ...ADR repositories (adr-tools, MADR)?

ADRs are exactly what `product/decisions/` is. Archeia subsumes ADR tooling rather than replacing it — you can use any ADR convention (MADR, Nygard, Y-statements) inside `product/decisions/*.md`, and the kernel's accumulating-record shape handles the append-only, supersession, and never-delete rules ADRs need.

If you're already using adr-tools, migrating to Archeia means moving your ADR directory to `product/decisions/` and adding the four frontmatter fields the accumulating-record schema requires (`title`, `created`, `status`, `supersedes`/`superseded_by`). That's the whole migration.

### ...Claude Code skills or Cursor rules or GitHub Copilot instructions?

Those are writers. Archeia is the substrate writers produce and consume. You can use Claude Code skills to populate `.archeia/`, use Cursor to read it in sessions, and use GitHub Copilot to consume it — they all work on the same tree as long as they obey the schemas.

The kernel is framework-neutral by design. It's what makes Archeia an open standard rather than a Claude Code plugin.

---

## Structural questions

### Why `.archeia/` and not `.context/` or `.docs/`?

"Archeia" comes from the Greek word for archives — a place where authoritative records are kept. The name signals intent: this is the canonical knowledge store, not a generic docs folder. The dot prefix keeps it out of the way in file explorers while remaining visible to agents.

### Can I use only some domains?

Yes. The five domains are the canonical software answer, but not every project uses all of them. A weekend side project might only have `product/` and `execution/` populated, with `business/`, `growth/`, and `codebase/` sitting mostly empty. The kernel requires all five to exist (conformance rule) but allows any of them to be nearly empty in practice.

**Why not make the five optional?** Because the habit of "just add a domain when you need it later" leads to drift and per-project variation, and that defeats the point of a standard. Committing to the five means a tool written against Archeia knows exactly where to look in any conforming project.

### What if I use a different project management tool (Jira, Linear)?

You have three options:

1. **Skip `execution/` entirely.** The other four domains still work. You lose the ability for agents to see task state, but you keep your existing tooling.
2. **Sync both ways.** Run a bridge that syncs between `.archeia/execution/` and your external tool. The agents read the markdown; the humans use the GUI.
3. **Use Archeia execution as the source of truth.** Write tasks in `.archeia/execution/tasks/` and let agents and the operator both work against the markdown. This is what Archeia Solo recommends.

### Is `.archeia/` committed to git?

Yes. The entire point is that project knowledge is versioned with the code. That said, some regenerable files (like `codebase/scan-report.md`) can be `.gitignored` if you prefer to regenerate them on CI rather than commit them — but the default is to commit everything.

### Can I use Archeia on a non-software project?

Technically yes — the kernel is domain-agnostic. Practically, the canonical software layout in `SCHEMA.md` won't fit. You'd want to write a new distribution with your own domains. Research labs, game studios, and consulting practices are all plausible targets for future distributions.

If you want to prototype a non-software distribution, use [`solo-builder.md`](../standard/distributions/solo-builder.md) as a template: pick your audience, pick your domains, pick your lifecycle shapes, pick your retention windows, ship your skills.

---

## Implementation questions

### How do humans interact with `.archeia/`?

In their normal editor (VS Code, Neovim, JetBrains, Zed, whatever). The files are plain markdown with YAML frontmatter — no special tool, no auth, no plugin required. Humans read them the way they read any other code file. Humans edit them by opening the file and typing.

When a human wants to search project knowledge, they use the same tools they use for code search: `grep`, `rg`, their editor's search panel. For queries over frontmatter specifically, `yq` plus `find` works; most of the time a path plus text search is enough.

### How do agents interact with `.archeia/`?

Through their normal file tools (`Read`, `Write`, `Edit`, `Glob`, `Grep` in Claude Code; equivalents in other frameworks). Nothing special is required. The frontmatter fields are YAML — any agent framework can parse them. The body is markdown — any agent framework can read it.

When an agent writes to `.archeia/`, it's expected to follow the schema for that domain and shape. Conformance is currently social (trust the skill) with kernel-level validation planned via `archeia:validate`.

### How do humans and agents avoid stepping on each other?

Primarily, they don't need to — most of the time the human is doing one thing and the agent is doing another. When they do touch the same file:

- **Git is the coordination layer.** Diffs are visible, conflicts surface on commit, revert is free, and every change has an author.
- **The ownership model prevents most overlaps.** Each domain has one writer family, so "the agent and I are both editing the product spec" is an expected case (both are product-owner writers), not a collision.
- **For transient artifacts (tasks), the status field makes work visible.** If a task is `active` and has `started: <timestamp>` in its frontmatter, the human can see the agent is working on it and stay clear.

For the edge case where both human and agent want to write the same file simultaneously, git does what it always does: merge cleanly if possible, surface a conflict if not. The human resolves the conflict the way they'd resolve any other code conflict.

### Does Archeia assume git specifically?

The kernel requires "persistent storage with history" and git is the reference implementation. In principle, jj, hg, or pijul would work — they all provide commit history, diffs, and branch-based async work. Practically, every current Archeia tool assumes git, and the standard's examples all use git. Other VCSes would need their own bridge code.

### Does it work with monorepos?

Yes. Put `.archeia/` at the monorepo root. If individual packages within the monorepo need their own scoped knowledge, that's a future extension — the kernel permits nested Archeia roots via cross-root contracts, but the current software application in `SCHEMA.md` assumes one root per repo.

### Does it work with polyrepo setups?

Partially. Each repo can have its own `.archeia/`, which handles per-repo knowledge. Cross-repo coordination (shared product spec across multiple downstream repos) is a future extension — the kernel's cross-root contract model is sketched but not implemented. For now, polyrepo teams should pick one "primary" repo (or a dedicated knowledge repo) and put `.archeia/product/` there, with downstream repos reading from it.

---

## Political questions

### Is Archeia free? Is it open-source? Who owns it?

The Archeia Standard is released under the MIT license. Anyone can implement it, extend it, ship distributions on it, or cite it in their own products. There is no governance body yet — as of Archeia 0.1.0, the author (Hugo Peck) maintains the spec. If the standard sees adoption beyond the reference distribution, a more formal governance structure will follow.

### Do I need permission to write a distribution?

No. The standard is open. Write a distribution, publish it, link to the kernel. If your distribution is useful, it'll get adopted; if not, it won't. No central approval.

### What if the spec is wrong about something?

Open an issue on the repo. The spec has a version (`standard/VERSION`), and breaking changes require a major version bump. Minor clarifications and additive changes happen continuously.

### Is this a product or a spec?

Both. The Archeia Standard is a spec. Archeia Solo is a distribution — a product you can install. They're separated deliberately so the spec can outlive any specific distribution.

---

## Still have questions?

- **Read the manifesto**: [`manifesto.md`](manifesto.md) — the one-page pitch
- **Read the principles**: [`../standard/PRINCIPLES.md`](../standard/PRINCIPLES.md) — the six fundamental truths
- **Read the kernel**: [`../standard/KERNEL.md`](../standard/KERNEL.md) — the formal substrate
- **Read the temporal model**: [`../standard/TEMPORAL_MODEL.md`](../standard/TEMPORAL_MODEL.md) — the three lifecycle shapes
- **Read Archeia Solo**: [`../standard/distributions/solo-builder.md`](../standard/distributions/solo-builder.md) — the reference distribution

Or just clone the repo and read the code:

```bash
git clone https://github.com/Hugopeck/archeia.git
cd archeia
```

It's small. Most of it is prose. You can read the whole thing in a sitting.
