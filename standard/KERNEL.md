# The Archeia Kernel

> **Claim:** the Archeia Kernel is the minimal substrate any conforming distribution extends. It defines the primitives, the invariants, the kernel operations, the inherent skills every distribution must provide, and the extension mechanism for adding new domains. It is deliberately small — small enough to read in one sitting, small enough to implement in a day, small enough to be non-negotiable.

The kernel is what you're citing when you say "this tool supports the Archeia Standard." The distributions are what you're citing when you say "this repo uses Archeia Solo." The two are different layers, and this document specifies the lower one.

---

## 1. Scope

The kernel defines:

- **Primitives** — the concepts every Archeia implementation must understand
- **Invariants** — the rules every conforming implementation must uphold
- **The three lifecycle shapes** — living, accumulating, transient
- **The five kernel operations** — `advance`, `complete`, `prune`, `supersede`, `evolve`
- **Inherent skills** — the skills every conforming distribution must provide (by its own name)
- **Inherent agents** — the agent roles every conforming distribution must provide
- **The extension mechanism** — how a distribution declares its domains, status vocabularies, retention windows, and ownership assignments
- **Validation** — how a tool checks that a repo conforms to the kernel

The kernel does **not** define:

- Which domains exist beyond a minimal `standard/` self-description (domain list is a distribution concern)
- Which format artifacts take beyond "text-native by default, binary-with-sidecar allowed"
- Which tool produces artifacts (agents, skills, scripts, humans — all permitted)
- Which VCS provides history (git is the reference implementation; any versioned storage works)
- Which approval workflow governs state transitions (policy, not spec)
- Which audience reads the artifacts (humans, agents, both — all permitted)

The [canonical software-project application of the kernel](SCHEMA.md) commits to five specific domains (`business/`, `product/`, `codebase/`, `growth/`, `execution/`) for software projects, but that commitment lives in `SCHEMA.md`, not here. The kernel itself is domain-agnostic above the minimum.

---

## 2. Primitives

Every Archeia implementation must understand these eight concepts:

### 2.1 Root

A **root** is a project root containing an `.archeia/` directory. A root is usually a git repository, but the kernel only requires "persistent storage with history" — any VCS (git, jj, hg, pijul) or even a versioned blob store qualifies. Git is the reference implementation.

### 2.2 Domain

A **domain** is a named subdirectory under `.archeia/` representing one knowledge area. Every artifact belongs to exactly one domain. The kernel does not fix the domain list — distributions declare their domains in a `standard/domains.yaml` file at the root. The [canonical software application](SCHEMA.md) commits to exactly five (`business/`, `product/`, `codebase/`, `growth/`, `execution/`).

### 2.3 Artifact

An **artifact** is a file inside a domain. Text-native by default: markdown, JSON, YAML, HTML. Binary artifacts are allowed only when paired with a `<file>.meta.yaml` sidecar carrying provenance, owner, schema version, and source.

Every artifact belongs to exactly one lifecycle shape (see §4).

### 2.4 Shape

A **shape** is one of three lifecycle categories every artifact belongs to:

- **Living** — edited in place, history in git, always current
- **Accumulating** — append-only record, status field tracks relevance, never pruned
- **Transient** — flows through status values with bounded retention, pruned when expired

The full specification of the three shapes is in `[TEMPORAL_MODEL.md](TEMPORAL_MODEL.md)`.

### 2.5 Owner

Every domain has exactly one **owner** — a writer family (a specific skill or an agent role) authorized to write to that domain. Owners are declared in the distribution's `standard/domains.yaml`.

One owner per domain. Many readers. Per Truth #4 in `[PRINCIPLES.md](PRINCIPLES.md)`, parallelism comes from subagent delegation, not concurrent writes.

### 2.6 Schema

A **schema** is the frontmatter and structural contract a domain's artifacts must satisfy. Schemas live as JSON Schema files under `standard/contracts/` and are enforced at write time by conforming writers and at validate time by the kernel `validate` operation.

The kernel ships base schemas for the three shapes (`living-doc.schema.json`, `accumulating-record.schema.json`, `transient-artifact.schema.json`) which specific artifact schemas extend.

### 2.7 Contract

A **contract** is a declared read relationship between two domains. For example: "Domain B reads artifact X from domain A, which guarantees frontmatter fields Y, Z and body sections P, Q." Contracts live as JSON Schema files under `standard/contracts/`.

The three contracts the [canonical software application](SCHEMA.md) enforces:

- `business/drafts/*.md` → `product/product.md` (via `draft.schema.json`)
- `product/product.md` → `execution/tasks/*.md` (via `product.schema.json`)
- `codebase/architecture/*.json` → `product/decisions/*.md` (via `c4.schema.json`)

### 2.8 Writer / Reader

A **writer** is anything that produces artifacts — agents, skills, scripts, humans. A **reader** is anything that consumes artifacts. The kernel is writer-agnostic and reader-agnostic. As long as writes conform to the schema and follow the ownership rules, the kernel doesn't care what produced them.

---

## 3. Invariants

Every conforming implementation MUST uphold these seven invariants. Violation of any one means the implementation is non-conforming.

1. **Knowledge lives in the root.** Artifacts are stored in `.archeia/` under the project root. Not in a wiki, not in a URL, not behind auth. In the root, versioned with the code, visible in every clone.
2. **Every artifact has exactly one owning domain.** No shared ownership, no multi-domain artifacts, no cross-domain writes.
3. **Every artifact has exactly one lifecycle shape.** Living, accumulating, or transient — pick one and follow its rules.
4. **Reads are free; writes are owner-only.** Any agent, skill, or human can read any artifact under `.archeia/`. Only the domain owner can write. Cross-domain coordination happens through reads of contract-conforming artifacts, not through cross-domain writes.
5. **Every factual claim cites a source.** Descriptive artifacts (scan reports, architecture docs derived from code, git history analyses) must cite the file paths or commits their claims come from. Prescriptive artifacts (vision, strategy, decisions) must cite their rationale and the prior artifacts they build on.
6. **Cross-domain dependencies are declared contracts, not inferred.** If domain B reads from domain A, there must be a JSON Schema under `standard/contracts/` describing the exact frontmatter and structure B relies on.
7. **History is preserved.** Living documents preserve history in git. Accumulating records preserve history on disk forever. Transient artifacts preserve history in git after pruning. No history is destroyed.

---

## 4. The three lifecycle shapes

See `[TEMPORAL_MODEL.md](TEMPORAL_MODEL.md)` for the full specification. This section defines only what the kernel requires.

A conforming implementation MUST:

- **Recognize all three shapes.** Every artifact type in every domain is assigned a shape.
- **Apply the shape's rules.** Living documents are edited in place. Accumulating records are append-only with the single permitted frontmatter mutation rule. Transient artifacts flow through status values and are pruned after retention.
- **Store history according to the shape.** Living → git. Accumulating → on-disk forever. Transient → on-disk during retention, git after.
- **Map status to temporal state for transient artifacts.** The distribution defines the mapping; the kernel requires one to exist.

---

## 5. The six kernel operations

Every conforming distribution MUST provide these six operations, either as skills the user can invoke by name or as functions the distribution's tooling calls internally. The kernel does not specify implementation — only the operation's contract.

Per [Truth #7 of PRINCIPLES.md](PRINCIPLES.md#7-latent-and-deterministic-work-belong-in-different-places), each operation is tagged as **latent** (judgment / synthesis, done by the model) or **deterministic** (mechanical, done by compiled code). Only `consolidate` is latent; the others are deterministic and should not burn LLM tokens.

### 5.1 `advance` — deterministic

**Applies to:** transient artifacts only.

**Effect:** promote an artifact from a status value that maps to `future` to one that maps to `present`. Record a `started` timestamp (or distribution-specific equivalent) in frontmatter.

**Example:** a task with `status: todo` (future) → `status: active` (present), `started: <now>`.

### 5.2 `complete` — deterministic

**Applies to:** transient artifacts only.

**Effect:** promote an artifact from a status value that maps to `present` to one that maps to `past`. Record a terminal timestamp in frontmatter (e.g., `completed`, `cancelled_at`, `concluded`). This timestamp starts the retention clock.

**Example:** a task with `status: active` → `status: done`, `completed: <now>`.

### 5.3 `prune` — deterministic

**Applies to:** transient artifacts only.

**Effect:** delete an artifact from disk whose retention window (distribution-defined, per artifact type) has elapsed since its terminal timestamp. The deletion is a git commit so the file is preserved in history.

**Example:** a task with `status: done`, `completed: 2026-03-29T16:45:00Z` and a 14-day retention window is pruned on or after 2026-04-12.

### 5.4 `supersede` — deterministic

**Applies to:** accumulating records only.

**Effect:** replace one record with a newer one. Write the new record with frontmatter `supersedes: <old-path>`. Perform the single permitted frontmatter mutation on the old record: update its `status` from `active` to `superseded` and add `superseded_by: <new-path>`. Both records remain on disk forever.

**Example:** ADR `20260115-row-level-security.md` is superseded by `20260801-schema-per-tenant.md`. Both files stay on disk; the old one has `status: superseded`.

### 5.5 `evolve` — deterministic

**Applies to:** all shapes, with different semantics per shape.

**Effect:** return the history of a named concept.

- **Living:** `git log <path>` — walk commit history.
- **Accumulating:** walk the `supersedes:` / `superseded_by:` chain on disk.
- **Transient:** walk recent past-state artifacts on disk (during retention) and fall back to `git log` for older history.

The operation's return type is distribution-defined (a structured list, a timeline, a diff view) but the contract is consistent: "show me how this thing changed over time."

### 5.6 `consolidate` — latent

**Applies to:** living documents and accumulating records. Never produces transient artifacts — consolidation outputs are meant to persist.

**Effect:** read a set of source artifacts (files, git history, external data, prior `.archeia/` artifacts) and produce or update a target artifact that integrates their content with cited evidence.

**Academic grounding:** this operation implements **memory consolidation** in the cognitive-science sense (Müller & Pilzecker 1900; Squire & Alvarez, *Current Opinion in Neurobiology* 5:169–177, 1995) — the process by which labile, detail-rich traces become stable, structured knowledge. In current LLM-agent literature the operation is typically called **"knowledge consolidation"** and is used throughout MemoryAgentBench (Hu et al., arXiv:2507.05257, 2025) and the Agent-Memory Survey. Earlier drafts of this kernel used the term "diarize" from Garry Tan's "Thin Harness, Fat Skills" (X, April 10, 2026); that term was a misapplied metaphor from speech-processing speaker diarization (Tranter & Reynolds, *IEEE TASLP* 14(5), 2006), which means something completely different. The term has been corrected to `consolidate` as of kernel version 0.2.0. See [`ONTOLOGY.md`](ONTOLOGY.md) §4.6 for the full history.

**Contract:**

1. **Inputs**: a set of source artifacts (paths, git refs, external data sources) and a target artifact path.
2. **Target shape constraint**: the target MUST be a living document or an accumulating record. Transient artifacts are not valid consolidation targets.
3. **Evidence rule**: every substantive claim in the target MUST cite at least one source from the inputs. Claims that cannot be evidenced must be flagged in-line with `<!-- INSUFFICIENT EVIDENCE: [description] -->` rather than fabricated.
4. **Idempotence**: semantically idempotent. Two runs of the same consolidation over the same inputs must produce semantically equivalent outputs; the exact prose may differ because the operation is latent, but the set of claims and citations must be the same up to paraphrase.
5. **Bi-temporal metadata**: when consolidating into a living document, the operation MUST update the target's `last_verified` frontmatter field to the current timestamp. This gives readers a staleness signal: a living document whose `last_verified` is months old is less trustworthy than one verified today.
6. **Latent budget warning**: consolidation is the only kernel operation that burns LLM tokens. Distributions should track consolidation frequency and cost, and skill authors should keep consolidation scopes narrow — large consolidations produce worse output and cost more.

**Examples:**

- `archeia:write-tech-docs` reads source files, config, and git history, and consolidates them into `.archeia/codebase/architecture/architecture.md`. Every architectural claim cites at least one source file path.
- `archeia:scan-git` reads git history and consolidates it into `.archeia/codebase/git-report.md`. Every claim about contributors or churn cites the git log.
- `archeia:review-draft` reads a `business/drafts/*.md` proposal plus `.archeia/codebase/architecture/` and consolidates them into updates to `.archeia/product/product.md` plus a new entry in `.archeia/product/decisions/`.
- `archeia:clarify-idea` reads the operator's rough idea, prior drafts, and optionally landscape research, and consolidates them into a new business draft.

Most of what Archeia skills actually do is consolidation. Naming the operation explicitly makes it possible to specify its contract, measure its cost, and audit its evidence discipline.

---

## 6. Inherent skills

Every conforming distribution MUST provide these six skills under its own namespace. A distribution named `archeia-solo` provides `archeia:init`, `archeia:validate`, etc. A future `archeia-research` distribution would provide the same operations under the same names.

| Skill | Latent / Deterministic | What it does |
| --- | --- | --- |
| **`archeia:init`** | Deterministic | Scaffold `.archeia/` for a new project. Creates the domain directories per the distribution's `standard/domains.yaml`, writes a default `standard/SCHEMA.md` pointer, creates a `standard/VERSION` file, and copies in the contract schemas. Idempotent — running on an existing root is a no-op plus a validation pass. |
| **`archeia:validate`** | Deterministic | Walk `.archeia/`, check every artifact against its domain's shape and schema, verify cross-domain contracts, check that all transient artifacts have valid status values per the distribution's status vocabulary, verify ownership is respected. Report conformance issues with file-path citations. |
| **`archeia:advance`** | Deterministic | The `advance` kernel operation. |
| **`archeia:complete`** | Deterministic | The `complete` kernel operation. |
| **`archeia:prune`** | Deterministic | Walk all transient artifacts, identify expired ones (past-state status with terminal timestamp + retention window elapsed), and delete them. Each deletion is a git commit. Distributions may wrap this as a scheduled maintenance skill. |
| **`archeia:consolidate`** | **Latent** | The `consolidate` kernel operation. Distributions typically implement this as multiple specialized skills (e.g., `archeia:write-tech-docs`, `archeia:scan-git`, `archeia:clarify-idea`, `archeia:review-draft`) rather than as a single generic skill. A generic `archeia:consolidate` is optional; specialized consolidation skills that honor the `consolidate` contract are required. |

`supersede` and `evolve` are **optional inherent skills** — recommended for convenience but not mandatory. A distribution may inline their effects into other skills (e.g., `review-draft` internally supersedes a prior decision).

---

## 7. Inherent agents

Every conforming distribution MUST provide this one agent role, with a system prompt that handles the temporal-state transitions for the distribution's artifacts:

### `archivist`

**Role:** manages past-state transitions, supersession decisions, and retention policy.

**Reads:** the full `.archeia/` tree.

**Writes:** frontmatter mutations on accumulating records (the one permitted edit), invocations of `archeia:complete` and `archeia:prune` on transient artifacts.

**Invoked when:** the user asks "how did we get here," "supersede decision X with Y," "prune finished tasks," or when a maintenance schedule fires.

The archivist is the one agent role that exists because of the kernel's temporal semantics, not because of any distribution's specific workflow. Every distribution needs one.

A distribution MAY provide additional agent roles (`librarian`, `conductor`, and others) but only `archivist` is required by the kernel.

---

## 8. The extension mechanism: declaring a distribution

A distribution extends the kernel by providing four things:

### 8.1 A `standard/domains.yaml` file

Declares which domains exist, who owns each, what shapes are permitted in each, and what contracts the distribution enforces.

```yaml
distribution: archeia-solo
version: 1.0.0

domains:
  - id: business
    owner: business-skills
    shapes: [living, accumulating, transient]
    reads: []
  - id: product
    owner: product-skills
    shapes: [living, accumulating]
    reads: [business, codebase]
  - id: codebase
    owner: codebase-skills
    shapes: [living]
    reads: [product]
  - id: growth
    owner: growth-skills
    shapes: [living, accumulating, transient]
    reads: [business, product]
  - id: execution
    owner: execution-skills
    shapes: [accumulating, transient]
    reads: [product, codebase]

contracts:
  - from: business
    to: product
    schema: standard/contracts/draft.schema.json
  - from: product
    to: execution
    schema: standard/contracts/product.schema.json
  - from: codebase
    to: product
    schema: standard/contracts/c4.schema.json
```

### 8.2 Status vocabularies and temporal mappings for transient artifacts

For every transient artifact type, declare:

- Status vocabulary (e.g., `todo, active, done, cancelled`)
- Status → temporal mapping (`todo → future`, `active → present`, `done → past`)
- Retention window (e.g., 14 days after terminal status)
- Terminal timestamp field name (e.g., `completed`)

Declared alongside the domain entries in `standard/domains.yaml` or in a separate `standard/lifecycles.yaml` — the kernel doesn't care which file, only that the information exists and is machine-readable.

### 8.3 JSON Schemas under `standard/contracts/`

Enforceable schemas for every artifact type the distribution uses. At minimum:

- The kernel's three base schemas (`living-doc.schema.json`, `accumulating-record.schema.json`, `transient-artifact.schema.json`)
- The distribution's cross-domain contract schemas (e.g., `draft.schema.json`, `product.schema.json`, `c4.schema.json`)
- Any per-artifact-type schema the distribution wants to enforce (e.g., `task.schema.json`, `adr.schema.json`)

### 8.4 Implementations of the six inherent skills and the archivist agent

The distribution ships `archeia:init`, `archeia:validate`, `archeia:advance`, `archeia:complete`, `archeia:prune`, `archeia:consolidate` (or its specialized consolidation skills), and an `archivist` agent. These can be implemented as skill files (for agent frameworks) or as scripts (for CI) — the kernel only cares that they exist and honor the operation contracts.

---

## 9. Where the harness fits

Archeia is the contract for the **knowledge layer**: where artifacts live, who owns them, how they evolve. Below the knowledge layer is the **execution layer**, where skills run inside a **harness** — a runtime that loads skill files, invokes the model, manages context, enforces safety, and reads/writes the filesystem. Claude Code, Cursor, OpenCode, custom CLI loops, and bespoke agent frameworks are all harnesses.

**Archeia is harness-agnostic.** Any harness that produces and consumes conforming `.archeia/` trees is interoperable with Archeia, regardless of its language, framework, or model provider.

The term "harness" is industry coinage that has crossed into academic literature. Recent papers that use it formally include Meta-Harness (Lee et al., arXiv:2603.28052, 2026), Natural-Language Agent Harnesses (arXiv:2603.25723, 2026), AutoHarness (arXiv:2603.03329, 2026), and OpenDev's 81-page technical report (arXiv:2603.05344, 2026). The field has settled on "harness" as the term for this layer, and Archeia adopts it. See [`ONTOLOGY.md`](ONTOLOGY.md) §7 for the full citation survey.

### The one hard requirement Archeia places on harnesses

The harness owns **compaction** — the moment when the context window fills up and the model summarizes its working state to continue. Compaction is memory triage; whatever doesn't survive is lost. This is a harness concern, not Archeia's concern. But the harness must respect one invariant:

> **Writes to `.archeia/` MUST be flushed to disk before compaction may discard them from in-context state.**

If a harness compacts away a pending write to `.archeia/product/product.md`, that's a harness bug, not an Archeia problem. The filesystem is the durable store; the harness's working memory is ephemeral by design. Compaction policy and persistence guarantees are separate concerns, and the kernel draws this line explicitly so that harness authors know where their responsibility ends and Archeia's begins.

### What must survive compaction

- **References to `.archeia/` paths the next turn will re-read from disk.** The harness must retain enough context for the next turn to know which files to re-open.
- **Any in-flight write that has not yet been committed to disk.** Either the write happens and the commit is visible to future turns, or the write never happened. No half-states.

### What can be lost at compaction

- Ephemeral reasoning traces, intermediate scratch
- Tool-call logs that are already persisted elsewhere (e.g., in the harness's own session log)
- Anything that has been consolidated into a durable artifact in the last turn

This division of labor is consistent with Sarah Wooders' framing in "Why memory isn't a plugin (it's the harness)" (X, April 4, 2026): *"Asking to plug memory into an agent harness is like asking to plug driving into a car. Managing context, and therefore memory, is a core capability and responsibility of the agent harness."* The harness manages what lives in the context window at any moment; Archeia provides the durable substrate the context window reads from and writes to. Neither layer replaces the other. This framing is also the core argument of Harrison Chase's "Your harness, your memory" (LangChain Blog, April 11, 2026), which makes the case that closed harnesses yield memory ownership to third parties and that open harnesses are the necessary response — an argument Archeia's open-standard approach aligns with directly.

### Why this matters

Without this boundary, the two layers fight each other. If a harness tries to manage persistent memory by keeping everything in context (bloat), or if Archeia tries to specify what the context window looks like (scope creep), both fail. Drawing the boundary here — Archeia owns durable, harness owns ephemeral, compaction must not drop pending durable writes — lets both layers do their jobs without stepping on each other.

---

## 10. Skill format (parameterized procedures)

Skills are procedural-memory artifacts that live **outside** `.archeia/` (typically in `skills/`, not a kernel concern where). A skill is a Markdown document with YAML frontmatter that teaches the model how to execute a specific workflow. The kernel specifies the minimum frontmatter shape.

### Required frontmatter fields

```yaml
---
name: <skill-name>
description: <trigger sentence for automatic invocation via description-matching>
---
```

Only `name` and `description` are strictly required. `name` must be unique within the distribution's namespace. `description` is the trigger text used by harnesses that support automatic skill selection (Claude Code, Cursor, etc.) — agents match user intent against skill descriptions to decide which skill to invoke.

### Recommended frontmatter fields

```yaml
---
name: review-draft
description: ...
version: 0.1.0
parameters:
  - name: draft_path
    type: file
    required: true
    description: Path to the business draft under .archeia/business/drafts/
  - name: codebase_context
    type: directory
    required: false
    default: .archeia/codebase/architecture/
reads:
  - .archeia/business/drafts/
  - .archeia/codebase/architecture/
writes:
  - .archeia/product/product.md
  - .archeia/product/decisions/
operation: consolidate
---
```

The `parameters` field is a refinement adopted from Garry Tan's "Thin Harness, Fat Skills" essay (X, [April 10, 2026](https://x.com/garrytan/status/2042925773300908103)) and supported by recent literature on atomic skills (Ma et al., arXiv:2604.05013, 2026). The core insight is that **skills are method calls with typed parameters, not undifferentiated prompts**. The same `/investigate` skill with different parameters produces radically different behaviors. Making this explicit lets harnesses validate inputs at invocation time and lets skill authors reason about reuse. Tan's own reference implementation is [gstack](https://github.com/garrytan/gstack) — 23 Claude Code skills organized as a virtual engineering organization.

The `reads` and `writes` fields declare the skill's `.archeia/` footprint. The `operation` field names which kernel operation the skill implements. These fields are not required for backward compatibility, but distributions that ship new skills are strongly encouraged to populate them, and kernel version 1.0 may make them mandatory.

### Skill invocation is harness business

How a skill gets invoked — automatic description-matching, explicit slash command, programmatic API call, scheduled cron — is the harness's concern. The kernel only specifies the file format and semantics.

---

## 11. Validation: what makes a repo conforming

A repo is **kernel-conforming** if `archeia:validate` passes with no errors against it. Validation checks:

1. `.archeia/` exists at the project root
2. `standard/domains.yaml` exists and declares at least one domain
3. `standard/VERSION` exists and is a valid semver string
4. Every artifact under `.archeia/` belongs to a declared domain
5. Every artifact has a declared shape and conforms to that shape's base schema
6. Every artifact conforms to any applicable artifact-type schema
7. Every cross-domain read is backed by a contract schema and the referenced artifacts satisfy it
8. Every transient artifact has a valid status per the domain's status vocabulary
9. Every transient artifact in a terminal status has a terminal timestamp
10. Ownership is respected: inspect git history for writes to each domain and confirm they come from the declared owner (this check is advisory — git blame doesn't always identify writer families)

A repo is **distribution-conforming** if it's kernel-conforming AND it satisfies the additional rules of its declared distribution (specific domain layout, specific skill roster, specific retention windows, etc.). The [canonical software distribution](SCHEMA.md) and [Archeia Solo](distributions/solo-builder.md) both add such rules.

---

## 12. What the kernel explicitly does not do

The kernel is small by design. It does not:

- **Define a universal domain list.** Five domains is a software-project commitment; other fields pick their own.
- **Mandate a specific agent framework.** Claude Code, Cursor, custom loops — all fine as long as they produce conforming artifacts.
- **Provide a UI.** Humans use their editor; agents use their tools. No web dashboard, no SPA, no electron app. If a distribution wants to add a UI, it's a distribution concern.
- **Replace git.** Git is the history layer. The kernel assumes history exists; it does not provide history.
- **Define approval workflows.** "Who can advance a draft to locked?" is a policy question, not a kernel question. Distributions layer approval on top via status transitions tied to git PR reviews, human confirmation, or automated checks.
- **Provide search, full-text indexing, or embeddings.** The kernel is not a knowledge graph or a vector store. If you want search, glob and grep are the default; layer anything fancier on top yourself.

The kernel stays small so it can be implemented in a weekend, so it can be cited by tools from different vendors without intellectual-property friction, and so it can survive ten years of changing agent frameworks without needing a major version bump.

---

## 13. Versioning

The kernel uses semantic versioning. `standard/VERSION` at the repo root contains the kernel version the repo pins. A conforming tool reads this version and either processes the repo (if it supports that version) or refuses with a clear error.

- **Major version bump** — breaking changes to primitives, invariants, operations, or inherent skills.
- **Minor version bump** — additive changes: new optional fields, new optional operations, new validation checks that don't break existing conforming repos.
- **Patch version bump** — clarifications, documentation fixes, or non-normative additions.

The current kernel version is **0.2.1**. The 0.1 → 0.2 bump reflected the addition of `consolidate` as a sixth operation (renaming the earlier `diarize` term per the ontology work), the addition of Truth #7 (latent vs deterministic) to PRINCIPLES.md, the addition of the harness boundary section (§9), and the parameterized-skill format refinement (§10). The 0.2.0 → 0.2.1 patch bump corrects attribution errors across the ontology and audit docs: the "Thin Harness, Fat Skills" essay is by **Garry Tan** (not Steve Yegge, who was only quoted in it); the verified Sarah Wooders quote from "Why memory isn't a plugin (it's the harness)" is now cited correctly; Harrison Chase's "Your harness, your memory" (LangChain Blog) is now cited directly; and Michael Chomsky's analysis essay (which introduced the four-memory-competencies audit framework via MemoryAgentBench) is now cited separately from Harrison Chase's essay. The kernel will reach **1.0.0** when the first external distribution (not Archeia Solo) is shipped and the kernel has survived that contact with a new audience.

---

## 14. Summary

The Archeia Kernel is eight primitives, seven invariants, three lifecycle shapes, six operations, six inherent skills, one inherent agent role, a harness boundary spec, a skill format spec, and one extension mechanism. Every conforming distribution extends it by declaring domains, contracts, and retention windows; every tool interoperable with Archeia implements the kernel operations against the distribution's schemas.

Everything else in the Archeia Standard — the specific domains, the specific skills, the specific ethos, the specific workflow — lives above the kernel in a distribution. The kernel's job is to be the smallest thing that makes all of that possible, so that many distributions can coexist without fighting each other, and so that tools from different vendors can compose on the same `.archeia/` tree without adapter code.

If you're implementing a tool that claims to support the Archeia Standard, this document is what you cite. If you're extending Archeia for a new audience or domain, this document is what you extend. Everything else is layered on top.