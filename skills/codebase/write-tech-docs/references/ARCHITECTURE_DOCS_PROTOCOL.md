# The Architecture Docs Protocol

A protocol for generating and maintaining structured architecture documentation
in the `.archeia/` directory.

---

## The Fragmentation Problem

Software teams produce architecture documentation in dozens of places: wiki
pages, Confluence spaces, Google Docs, Notion databases, Lucidchart boards,
whiteboard photos in Slack, "architecture" sections buried in root READMEs,
and comments in code that nobody reads twice. Some of it is accurate. Most of
it isn't. None of it lives next to the code.

When a developer needs to understand the system, they don't consult the wiki —
they read code, ask a colleague, or guess. When an AI coding agent needs to
understand the system, it has nothing. It sees file names and import statements
and infers what it can. It gets the topology wrong, invents dependencies that
don't exist, and misidentifies the tech stack because it read an outdated
README instead of the manifest.

The problem isn't that teams don't document. The problem is that documentation
lives outside the repository, detached from the code it describes. It's
written once and abandoned. It drifts from reality within weeks.

**Architecture documentation belongs in the repository, next to the code,
generated from evidence, and maintained by the same agents that write the
code.**

That is what `.archeia/` is. A directory of structured architecture documents,
each generated from real files — manifests, configs, imports, schemas — with
every claim citing a file path as evidence. Not a wiki page someone wrote
from memory. Not a diagram someone drew from a mental model. Documentation
that is provably true because it cites its sources.

---

## Why `.archeia/`

Architecture documentation needs a home that is:

- **In the repository.** Not a wiki, not a shared drive, not a URL that
  requires a separate login. In the repo, versioned with the code, visible
  in every clone.
- **Separate from code.** Not scattered across README.md files, not buried in
  inline comments. A dedicated location that agents and humans know to check.
- **Structured, not freeform.** Templates define what each document covers,
  ensuring consistency across projects and preventing the "wall of prose"
  failure mode.
- **Generated, not authored.** The skill reads real files and produces
  documentation from evidence. Humans review and refine; they don't start
  from a blank page.

The `.archeia/` directory is that home. It sits at the repository root,
contains a known set of documents, and is the single location for system-level
architecture information. Colocated READMEs handle directory-level context.
`agents.md` handles directory-level rules. `.archeia/` handles the system view.

---

## What Goes In

The `.archeia/` directory contains three categories of documents, each serving
a different audience and purpose.

### Prose Documents (human-readable architecture)

**Architecture.md** — The system-level map. What this project is, how it's
structured, what the major modules are, how data flows through the system.
This is the document a new engineer reads on day one to understand the shape
of the codebase. It includes topology, module boundaries, and the primary
data flow — structured as a table with source, target, message, type, and
protocol columns so downstream tools can consume it programmatically.

It also includes conditional sections for data model (entities and
relationships when an ORM is detected) and state lifecycles (when state
machines or lifecycle enums are found).

**Standards.md** — How code is written here. Language version, formatter,
linter, test runner, naming conventions. The things that change infrequently
and apply across the whole codebase.

**Guide.md** — How to operate the project. Setup steps, dev commands, test
commands, deployment workflow. The operational handbook.

### Structured Data (machine-readable models)

**System.json** — C4 Level 1. The system as a single entity, surrounded by
people who use it and external systems it depends on. Every entity cites
evidence from the actual codebase.

**Containers.json** — C4 Level 2. The major runtime units inside the system
boundary — API servers, workers, databases, caches — when they can be
identified with evidence. These are processes, not source directories.

**Components.json** — C4 Level 3. The internal structure of each generated
container — routes, middleware, services, models — when evidence-backed
internal modules can be identified. Code-level modules and their
relationships.

**DataFlow.json** — Structured interaction records for the primary request
or interaction path through the system when one can be traced with evidence.
Each step has a source, target, message, type (sync/async/response), and
protocol. This is the machine-readable source that sequence diagrams render
from.

**Entities.json** (conditional) — Domain entities extracted from ORM schemas
or model definitions. Fields, types, constraints, and relationships with
cardinality. Generated only when schema evidence exists.

**StateMachine.json** (conditional) — State lifecycles for domain entities
with explicit state transitions. States, triggers, guards. Generated only
when state machine libraries or clear lifecycle enums are detected, and only
with high or medium confidence.

### The Relationship Between Prose and Data

Architecture.md and the JSON files are not redundant. They serve different
audiences through different lenses of the same system:

- Architecture.md describes the system in prose for humans to read and
  understand. Its Data Flow table is structured enough for tools to consume
  but readable enough for a meeting.
- The C4 JSONs model the system as structured data for tools to process —
  diagram generators, validation scripts, architecture linters. They are
  not designed to be read directly.
- DataFlow.json is the structured version of Architecture.md's Data Flow
  table. Architecture.md is human-first; DataFlow.json is machine-first.
  When an evidence-backed flow can be traced, they describe the same
  interactions. When it cannot, Architecture.md records the insufficiency and
  DataFlow.json is omitted.

**Architecture.md is generated first.** The C4 JSONs, DataFlow.json,
Entities.json, and StateMachine.json refine and structure what Architecture.md
describes in prose. If they contradict each other, Architecture.md is wrong
— the JSONs are generated from deeper analysis with stricter evidence
requirements.

---

## What Stays Out

| Content | Where it belongs | Why not `.archeia/` |
|---------|-----------------|---------------------|
| Directory-level context | Colocated README.md | Scoped to one directory, not the system |
| Agent imperative rules | Colocated agents.md or root AGENTS.md | Rules, not architecture |
| Accumulated learnings and dead ends | README.md Learnings section | Grows organically, not generated from evidence |
| API endpoint reference | Generated docs / OpenAPI spec | Changes with every route, too volatile |
| Architecture decision records | ADRs / DECISIONS.md | Explains *why*, not *what* |
| Rendered diagrams (Mermaid) | `.archeia/codebase/diagrams/` via archeia:draw-diagrams | Diagrams are views over this data, not the data itself |
| Root README | Root README.md | Project identity, not architecture |

The principle: `.archeia/` contains what can be generated from evidence.
Knowledge that accumulates through work (learnings, decisions, context) belongs
in READMEs and ADRs. Rules for agents belong in agents.md.

---

## The Evidence Principle

Every claim in every `.archeia/` document must cite a file path. This is the
single most important rule in the protocol.

Why evidence matters:

- **Verifiable.** A reviewer can check every claim by reading the cited file.
  No trust required.
- **Maintainable.** When evidence changes (a dependency is removed, a file
  is renamed), the citation becomes stale and the claim can be flagged or
  removed. Documentation that doesn't cite evidence can be wrong forever.
- **Generatable.** An AI agent can produce evidence-grounded documentation
  by reading real files. It cannot produce accurate documentation from
  general knowledge about frameworks.
- **Honest.** When evidence is insufficient, the template requires marking it:
  `<!-- INSUFFICIENT EVIDENCE: [what is missing] -->`. A gap is better than
  a guess.

The skill validates evidence in Phase 3 (Self-Validation): every cited file
path is checked with Glob. Fabricated paths are removed. This means the
generated docs are as accurate as the skill's ability to read the codebase —
and no more accurate.

---

## The Template-as-Exemplar Pattern

The templates in `assets/templates/` are not blank forms to fill in. They are
structural exemplars — complete example documents that show the exact shape
the generated output should take.

For Markdown templates (Architecture.md, Standards.md, Guide.md):
- YAML frontmatter defines metadata: `layer`, `depends_on`,
  `required_evidence`, `validation`
- The body defines required sections, conditional sections, inference signals,
  quality rubrics, and anti-patterns
- The frontmatter is consumed by the skill — it does NOT appear in output

For JSON templates (System.json, Containers.json, Components.json,
DataFlow.json, Entities.json, StateMachine.json):
- The template IS the example — it contains realistic data for a fictional
  Task Management API
- The skill reads the template, understands the structure, and produces
  output following the same shape with real data from the target repository
- Field names, nesting, and types must match exactly

Every output also has a generation disposition in the skill protocol:
- `always_generated` — write the file on every run and record gaps inside it
- `always_attempted` — read the template on every run, but write the file only
  when the required structure can be evidenced; otherwise emit an explicit
  insufficiency outcome and skip the file
- `conditional` — attempt only when a triggering evidence class exists

This pattern serves two purposes:
1. **The skill has an unambiguous target.** It doesn't interpret free-text
   instructions about what to generate — it sees the exact output shape.
2. **The template is self-documenting.** Reading the template shows you
   exactly what the output looks like without running the skill.

---

## Separation of Concerns Across Archeia Skills

`.archeia/` docs are one layer in a multi-layer documentation system. Each
layer has a distinct purpose and audience:

| Layer | Files | Purpose | Audience |
|-------|-------|---------|----------|
| System architecture | `.archeia/` docs | What the system is, how it's structured | Engineers onboarding, agents planning structural changes |
| Directory knowledge | Colocated README.md | What this directory does, how it's organized, what was learned | Anyone working in a directory |
| Agent rules | Colocated agents.md + claude.md | Local imperative instructions for agents | AI coding agents |
| Diagrams | `.archeia/codebase/diagrams/` | Visual rendering of structured data | Meetings, reviews, stakeholders |
| Root identity | Root README.md, AGENTS.md, CLAUDE.md | Project overview and agent entry point | First-time visitors, agents starting work |

The boundaries between layers:
- **`.archeia/` describes the system.** READMEs describe directories.
- **`.archeia/` is generated from evidence.** READMEs accumulate knowledge
  through work.
- **`.archeia/` is disposable.** It can be regenerated from scratch without
  losing information (unlike README Learnings sections, which are append-only
  and sacred).
- **`.archeia/` is the source data.** Diagrams are views rendered from it.

---

## Generation Order and Dependencies

The skill generates `.archeia/` docs in a specific order because later
documents depend on earlier ones:

```
Architecture.md          (no dependencies — generated from raw exploration)
    ↓
System.json              (references Architecture.md for system description)
    ↓
Containers.json          (references System.json for external systems)
    ↓
Components.json          (references Containers.json for container list)
    ↓
Entities.json            (conditional — references Architecture.md Data Model)
    ↓
DataFlow.json            (references Containers/Components for participant IDs)
    ↓
StateMachine.json        (conditional — references Entities.json for entity IDs)
    ↓
Standards.md             (may reference Architecture.md for topology context)
    ↓
Guide.md                 (may reference Architecture.md + Standards.md)
```

Each template participates in two scheduling decisions:
- dependency order (`depends_on` field or `level` number)
- generation disposition (`always_generated`, `always_attempted`, or
  `conditional`)

The skill respects both.

---

## Maintenance in the Agentic Era

`.archeia/` docs are fully regenerable. Unlike READMEs (which accumulate
learnings that can't be derived from code), every claim in `.archeia/` traces
to a file that still exists in the repository.

This means:
- **Full regeneration, not incremental updates.** When the system changes,
  rerun the skill. It reads the current state of the repo and produces fresh
  docs. No merge conflicts, no stale sections, no drift.
- **No manual edits.** If a human edits an `.archeia/` file directly, those
  edits are overwritten on the next regeneration. The fix is always: change
  the code or config, then regenerate.
- **Evidence expiration.** When a cited file is deleted or renamed, the next
  regeneration catches it in the validation pass and removes or updates the
  reference. Documentation can't cite files that don't exist.

This is deliberate. `.archeia/` documents are a projection of the codebase's
current state, not an independent artifact with its own lifecycle.

---

## Design Decisions

### `.archeia/` over `docs/`

A `docs/` directory is convention-free — it can contain anything from API
references to tutorial PDFs to architecture diagrams from 2019. `.archeia/`
is a known set of files with known structure. An agent or human knows exactly
what to find there without browsing.

### Prose first, then structured data

Architecture.md is generated before the C4 JSONs. This is intentional — the
prose document captures the system's shape in human-readable form, and the
JSONs refine specific aspects into machine-readable structure. If the skill
generated JSONs first, it would be harder to validate them without a prose
description to compare against.

### Evidence over inference

The skill could infer more. It could guess at deployment targets from
framework choice, or infer API patterns from directory naming conventions.
It doesn't. Every claim must cite a file. This makes the output less
comprehensive but more trustworthy. A gap marked `INSUFFICIENT EVIDENCE` is
more useful than a plausible guess that turns out to be wrong.

### Templates as examples, not schemas

JSON Schema validation would catch structural errors but wouldn't help the
skill understand what good output looks like. A complete example — with
realistic data, proper evidence citations, and the right level of detail —
teaches by showing. The skill reads the example and produces output that
looks like it.

### Conditional generation for domain-specific data

Not every project has an ORM, a database schema, state machines, an
obviously traceable primary interaction path, identifiable runtime units, or
component-level internal modules. Entities.json and StateMachine.json are
generated only when evidence supports them. Containers.json,
Components.json, and DataFlow.json are always attempted because many
repositories do expose those structures, but if any of them cannot be
evidenced the skill must emit an explicit insufficiency outcome instead of
fabricating the document. This prevents the skill from producing empty or
fabricated documents for projects where the data doesn't exist.

### Drawing from established approaches

This protocol draws from:
- **C4 Model** — the three-level zoom (System → Container → Component) and
  the principle that diagrams should be "just enough" detail at each level
- **Docs as Code** — documentation lives in the repo, versioned with the
  code, reviewed in PRs
- **Diátaxis** — the distinction between reference (Architecture.md),
  how-to (Guide.md), and explanation (READMEs) as separate documentation
  modes
- **arc42** — the idea that architecture documentation has a known structure
  with specific sections, not freeform prose
