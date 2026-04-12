# The Six Fundamental Truths

The Archeia Standard rests on six claims about how AI coding agents actually work — two about the problems agentic work hits today, and four about the substrate that dissolves them. Every design decision in the kernel — the directory layout, the ownership rules, the temporal model, the frontmatter schemas — follows from these six.

If any of the six turn out to be wrong, Archeia is wrong. They are load-bearing. They are what we're putting our names on.

---

## 1. Context is the bottleneck, not intelligence

Modern AI agents are not limited by reasoning power. GPT-5-class, Claude-4-class, and open-weight frontier models can all think rings around most software problems. What they cannot do is work on a problem they cannot see, remember a decision that was made before their session started, or trust a claim they cannot verify.

Every token an agent spends *finding* context — re-reading the codebase, re-deriving architecture, re-asking the user what the spec is — is a token not spent on actual work. Every time a session ends and a new one begins without a shared memory, the reconstruction tax is paid from scratch.

Structure is the cheapest intelligence multiplier available. Putting the right fact in a predictable location is worth more than swapping in a smarter model. A weaker agent with good context will out-ship a stronger agent without it, every time.

**Consequence:** the single most valuable thing you can do for an agentic system is write down what you know, where the agents can find it, in a format they can parse.

---

## 2. Human-agent collaboration is the second bottleneck

Finding context is only half the problem. The other half is what humans and agents can do *together*.

A chat window can hold a conversation, but it cannot hold a collaboration. Humans need to direct agents toward the right work, observe agents while they're working, intervene when agents go wrong, hand off work between sessions, recover from mistakes, and audit what happened and why. Agents need to persist their output somewhere a human can read it later, leave notes for the next agent that picks up the thread, and work in the background while the human does something else.

None of this fits in a chat transcript. When you try, every collaboration reverts to "type everything in the conversation," which doesn't scale past one session and one person.

What's missing is a **shared surface** — a board or canvas where both humans and agents can work on the same artifacts with guarantees:

- **Safely** — no accidental overwrite of someone else's work
- **Recoverably** — mistakes can be undone, not just lamented
- **Traceably** — every change records who made it, when, and why
- **Synchronously** — both can edit live, with the other seeing the change
- **Asynchronously** — either can work while the other is offline, and the work merges cleanly

Every agentic project that grows past a solo experiment hits this wall. Most respond by building a web UI, a project board, a real-time editor, or some combination. That's infrastructure you don't need.

**Consequence:** the standard has to serve both humans and agents on the same surface, not just give agents a memory.

---

## 3. The filesystem is already the database and the canvas

Truths #1 and #2 look like they require two separate systems: a memory service for agents and a collaboration surface for humans. The standard's claim is that **one substrate already does both, and you're installing infrastructure you don't need**.

**For agent memory, the filesystem is already a database:**

- Directories are tables
- Files are rows
- Paths are primary keys
- YAML frontmatter is schema
- Glob patterns are queries
- Git history is the audit log

**For human-agent collaboration, the filesystem is already a canvas:**

- Humans edit files in their editor (VS Code, Neovim, JetBrains, whatever)
- Agents edit files via tools (Read, Write, Edit)
- Git provides **atomic commits** (safety)
- Git provides **revert** (recovery)
- Git provides **log + frontmatter** (traceability — who, when, why)
- Git provides **branches** (asynchronous work)
- Git provides **diffs** (review surface)

The same tree — plain markdown files under a known schema — serves both. Humans read it the way they already read code. Agents read it the way they already read code. The collaboration surface and the memory layer are the same files.

The only thing missing is a convention about *where things go and who writes them*. That's the standard's entire job. Once the convention is in place, you have both an agent database and a human-agent workspace with zero additional infrastructure, zero auth layer, zero latency, zero operational cost.

**Consequence:** do not install a memory service. Do not install a collaboration tool. Do not spin up a vector DB. Structure your filesystem, write down the convention, and let git do the rest.

---

## 4. Ownership plus delegation is the concurrency model

Multi-agent systems raise a predictable question: what happens when two agents need to work on the same state at the same time? Most answers reach for locks, consensus protocols, CRDTs, or merge algorithms. All of them add complexity you never pay off.

Archeia's answer is simpler: **each domain has exactly one owner, and parallelism comes from delegation, not concurrency.**

The owner is a single authoritative writer — a specific skill or an agent-role authorized to write to that domain's portion of `.archeia/`. When the owner needs parallel work, it does not open its domain for concurrent writes. Instead, it delegates:

1. The owner reads the current state.
2. The owner identifies independent sub-tasks.
3. The owner spawns **subagents** in isolated context windows, one per sub-task.
4. Each subagent produces a structured output and returns it.
5. The owner integrates the outputs and commits them on its own authority.

Reads are free — any agent can read any file in `.archeia/` for context. Writes are owner-only. Parallelism is delegation, not concurrent access. There is no moment when two writers hold the same pen at commit time, because subagents *return results*; they don't *write to the tree*.

This is what the subagent primitive is for in Claude Code and every serious agentic framework. It's often framed as a context-management trick ("offload side work to a fresh window so your main thread stays clean"), but its deeper purpose is exactly this: giving a single authoritative writer the ability to do parallel work without becoming a multi-writer. Conflicts cannot happen at the file layer because the layer is, by construction, single-writer. The subagent primitive is the native concurrency model for domain ownership.

**Consequence:** you can run complex multi-agent pipelines against the same `.archeia/` tree without designing a coordination system, a lock manager, or a merge strategy. Assign one owner per domain; let the owner delegate. That's the entire coordination model.

---

## 5. Project knowledge comes in three lifecycle shapes: living, accumulating, transient

Not every artifact has the same lifecycle. Most project knowledge is living documents — one file per concept, edited in place, with history in git. A smaller but essential subset is accumulating records — ADRs, retros, concluded experiments — append-only artifacts that stay on disk forever because the record itself is the point. A minority is transient artifacts — tasks, drafts, running experiments — that flow through states during their lifetime and get pruned from disk after a bounded retention window, with git preserving the long tail.

This is the principle most in-repo knowledge systems miss, and the one we spent the most time getting wrong. Earlier drafts of the standard tried to treat every artifact as flowing through a uniform past/present/future lifecycle. That framing was elegant but false: it duplicated what git already does for living documents, it forced ADRs into a lifecycle they don't actually have, and it caused filesystem bloat as operational artifacts accumulated with no pruning story.

The three-shapes model is what falls out when you walk through the real artifacts honestly. Living documents (product.md, architecture.md, vision.md, scan-report.md — the bulk of `.archeia/`) are implicit-present — you edit them, git holds history, there's no state machine and no supersession files cluttering the directory. Accumulating records (product/decisions/, execution/retros/, business/landscape/) are append-only, with a `status` field tracking relevance (active/superseded/archived), and they are *never deleted*. Transient artifacts (execution/tasks/, execution/plans/, business/drafts/) have a real lifecycle with a retention window — they flow through status values that map to temporal categories, and once they reach a terminal state they sit on disk for a short retention period (Archeia Solo defaults: 14 days for tasks, 30 days for plans, 0 days for discarded drafts) before being pruned.

The kernel operations split cleanly by shape: `advance` and `complete` and `prune` apply only to transient artifacts; `supersede` applies only to accumulating records; `evolve` maps to `git log` for living documents and to on-disk traversal for the other shapes. Three shapes, five operations, one rule: match the machinery to the lifecycle the artifact actually has, and stop fighting git.

**Consequence:** most of `.archeia/` is living documents backed by git, which means the standard doesn't need a universal temporal state field, doesn't need supersession chains for most artifacts, and doesn't bloat over time. The minority of artifacts that genuinely need lifecycle tracking get it, with retention windows that match how humans actually work with operational state.

See [`TEMPORAL_MODEL.md`](TEMPORAL_MODEL.md) for the full specification — the three shapes, the status-to-temporal mapping for transient artifacts, the retention-window conventions, and worked examples across all five domains.

---

## 6. Agents compose via files, not APIs

When two agents need to work together, the default engineering answer is to define a protocol: an HTTP API, a message queue, a function signature, a shared type. All of them work. All of them are proprietary to the agent framework that defined them, which means agents from different frameworks cannot compose without adapter code.

Archeia's answer: **the filesystem is the message bus, and frontmatter is the schema.**

Agent A writes a file with documented frontmatter fields. Agent B's trigger is "when a file matching this path pattern and this frontmatter signature lands, do this work." There is no wire protocol. There is no RPC layer. There is no shared type library. The integration surface is the file convention.

This is what makes Archeia a genuinely open standard rather than a framework. An agent written in Python using a custom loop can produce `.archeia/business/drafts/foo.md`, and an agent written in TypeScript using Claude Code's SDK can consume it, and they never share a line of code. The only thing they share is the standard.

It also makes every integration transparent. Humans can read the handoff by opening the file. The state of the system is always inspectable with `ls` and `cat`. There is no "black box" in the agent pipeline because every intermediate step is a file sitting on disk with a timestamp.

**Consequence:** you can build multi-agent systems that span tools, frameworks, and languages without writing any integration code. As long as every participant obeys the standard, composition is free.

---

## The six truths together

Each principle is useful alone. Together they compound:

- **Truth #1** names the first bottleneck: context.
- **Truth #2** names the second bottleneck: human-agent collaboration.
- **Truth #3** names the substrate that dissolves both: the filesystem as database *and* canvas.
- **Truth #4** names the coordination model: ownership plus subagent delegation.
- **Truth #5** names the lifecycle model: three shapes (living, accumulating, transient), each with different rules.
- **Truth #6** names the composition model: files as the message bus.

Remove any one and the others break. Without naming both bottlenecks, there's no reason to adopt the substrate. Without the substrate, you end up building a memory service *and* a project board and gluing them together. Without ownership + delegation, you need a distributed coordination protocol. Without the three shapes, you either bloat the filesystem forever or delete artifacts that future work needs to reference — wiki rot eats you either way. Without file-based composition, you're back to framework lock-in and adapter code between every pair of agents.

The standard is what you get when you follow all six at the same time and let them collide. What falls out is Archeia.
