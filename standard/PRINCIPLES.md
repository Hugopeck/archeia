# The Five Fundamental Truths

The Archeia Standard rests on five claims about how AI coding agents actually work. Each is stated as a universal principle. Every design decision in the kernel — the directory layout, the ownership rules, the temporal model, the frontmatter schemas — follows from these five.

If any of the five turn out to be wrong, Archeia is wrong. They are load-bearing. They are what we're putting our names on.

---

## 1. Context is the bottleneck, not intelligence

Modern AI agents are not limited by reasoning power. GPT-5-class, Claude-4-class, and open-weight frontier models can all think rings around most software problems. What they cannot do is work on a problem they cannot see, remember a decision that was made before their session started, or trust a claim they cannot verify.

Every token an agent spends *finding* context — re-reading the codebase, re-deriving architecture, re-asking the user what the spec is — is a token not spent on actual work. Every time a session ends and a new one begins without a shared memory, the reconstruction tax is paid from scratch.

Structure is the cheapest intelligence multiplier available. Putting the right fact in a predictable location is worth more than swapping in a smarter model. A weaker agent with good context will out-ship a stronger agent without it, every time.

**Consequence:** the single most valuable thing you can do for an agentic system is write down what you know, where the agents can find it, in a format they can parse. That's all Archeia is.

---

## 2. The filesystem is already the database

Every serious project working with agents eventually reaches for persistent memory. The default answers are a vector database, a memory service, a knowledge graph, or a custom schema-on-top-of-SQL. All of them work. All of them are massively over-engineered for what the problem actually requires.

The filesystem already provides every primitive you need:

- **Tables** are directories
- **Rows** are files
- **Primary keys** are paths
- **Schema** is YAML frontmatter
- **Queries** are glob patterns
- **Audit log** is git history
- **Permissions** are ownership rules

The only thing missing is a convention for *where things go and who writes them*. That's the standard's entire job. Once that convention is in place, you have a database — addressable, queryable, versioned, human-readable, agent-parseable — with zero infrastructure, zero auth layer, zero latency, zero operational cost.

**Consequence:** do not install a memory service. Do not spin up a vector DB. Do not write an ontology. Structure your filesystem, write down the convention, and let git do the rest. If you later discover a case the filesystem genuinely cannot handle, *then* layer a specialized tool on top — but you will find that you never need to.

---

## 3. Ownership is the only concurrency primitive agents need

Multi-agent systems raise obvious coordination questions: what happens when two agents try to write the same file? What if one agent's output contradicts another's? How do you merge conflicting edits? Most answers reach for locks, conflict-free replicated data types (CRDTs), merge algorithms, consensus protocols, or transaction managers.

Archeia's answer is simpler: **assign each knowledge domain to exactly one writer family, and conflicts literally cannot happen.**

A writer family is a set of writers following the same schema and the same ownership rules. Two agents running the `archeia:clarify-idea` skill both belong to the business writer family — they can both write to `.archeia/business/drafts/`, and git resolves any accidental overlaps the same way it resolves accidental overlaps between two human contributors: by making one of them rebase.

Reads are free. Any agent can read any file in `.archeia/` for context. Writes are domain-scoped. A codebase agent never writes to the product domain. A product agent never writes to the execution domain. Cross-domain interaction happens through reads of frontmatter contracts, not through cross-domain writes.

This is the cheapest coordination primitive that works for multi-agent systems. It requires no runtime, no broker, no protocol. It's enforced by skill conventions, not by the filesystem itself, and it holds as long as the writer families honor their ownership.

**Consequence:** you can run many agents in parallel against the same `.archeia/` tree without designing a coordination system. The standard IS the coordination system.

---

## 4. Project knowledge has a temporal state: past, present, future

Every artifact in a project refers to a moment. Some artifacts describe what happened: retrospectives, git history analysis, completed tasks, superseded specs. Some describe what is: current architecture, active work, locked product spec. Some describe what is intended: draft vision, proposed designs, upcoming tasks.

This is the principle most in-repo knowledge systems miss. ADR repos, arc42 templates, Diataxis, and Docs as Code are all flat and present-tense. They have no theory of time. History is implicit in git log, intent is implicit in "TODO" comments, and the coexistence of "what we used to do" and "what we want to do" in the same documentation is what makes most wikis rot.

Archeia treats temporal state as a first-class field. Every artifact has `temporal_state: past | present | future` in its frontmatter. Transitions between states are kernel operations — `advance` (future → present) and `archive` (present → past). Walking the past-state chain of a concept gives you its evolution without needing a separate timeline system.

The temporal axis resolves cases the older "descriptive vs prescriptive" split fumbles: retros are past and authored, drafts are future and prescriptive, done tasks are past and operational. "When does this artifact refer to?" is a human-native question — everyone already thinks this way. "Is this regenerable?" is an engineer's question. The human question wins.

**Consequence:** Archeia has a native theory of project time. You can ask an agent "show me how the onboarding spec evolved over the last quarter" and the answer is a glob pattern plus a frontmatter filter, not a database query.

---

## 5. Agents compose via files, not APIs

When two agents need to work together, the default engineering answer is to define a protocol: an HTTP API, a message queue, a function signature, a shared type. All of these work. All of them are proprietary to the agent framework that defined them, which means agents from different frameworks cannot compose without adapter code.

Archeia's answer: **the filesystem is the message bus, and frontmatter is the schema.**

Agent A writes a file with documented frontmatter fields. Agent B's trigger is "when a file matching this path pattern and this frontmatter signature lands, do this work." There is no wire protocol. There is no RPC layer. There is no shared type library. The integration surface is the file convention.

This is what makes Archeia a genuinely open standard rather than a framework. An agent written in Python using a custom loop can produce `.archeia/business/drafts/foo.md`, and an agent written in TypeScript using Claude Code's SDK can consume it, and they never share a line of code. The only thing they share is the standard.

It also makes every integration transparent. Humans can read the handoff by opening the file. The state of the system is always inspectable with `ls` and `cat`. There is no "black box" in the agent pipeline because every intermediate step is a file sitting on disk with a timestamp.

**Consequence:** you can build multi-agent systems that span tools, frameworks, and languages without writing any integration code. As long as every participant obeys the standard, composition is free.

---

## The five truths together

Each of these principles is useful on its own. Together they compound:

- Truth #1 tells you **why** the standard matters (context is the limit).
- Truth #2 tells you **what** the substrate is (the filesystem).
- Truth #3 tells you **how** multiple agents coexist (ownership).
- Truth #4 tells you **when** each artifact applies (temporal state).
- Truth #5 tells you **how** agents hand off work (files as the message bus).

Remove any one and the others break. Without context primacy, there's no reason to write things down. Without the filesystem claim, you build a memory service. Without ownership, you need a coordination protocol. Without temporal state, you can't distinguish history from intent. Without file-based composition, you're back to framework lock-in.

The standard is what you get when you follow all five principles at the same time and let them collide. What falls out is Archeia.
