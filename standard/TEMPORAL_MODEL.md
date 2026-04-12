# The Lifecycle Model

> **Claim:** project knowledge comes in three lifecycle shapes — **living**, **accumulating**, and **transient** — and each one needs different handling. Most of `.archeia/` is living documents backed by git. A minority is accumulating records that stay on disk forever. A smaller minority is transient artifacts that flow through states and get pruned. The standard's job is to recognize which shape each artifact is and apply the minimum machinery required.

This document replaces the earlier past/present/future framing. That framing was elegant but wrong: it tried to universalize a lifecycle that most artifacts don't actually have, and it ended up duplicating what git already does perfectly for living documents. The three-shapes model is what falls out when you walk through the real artifacts honestly.

---

## 1. Three shapes of project knowledge

Every artifact in every Archeia domain belongs to exactly one of three shapes. The shape determines everything: whether it has a temporal state, whether it gets pruned, whether it supports supersession, how its history is stored, and which kernel operations apply to it.

| Shape | One-line definition | History lives in |
|---|---|---|
| **Living** | One file per concept, edited in place, always current | Git |
| **Accumulating** | Append-only records that never leave disk | The disk itself (all records stay) |
| **Transient** | Flows through states during its lifetime, then pruned | Disk during retention, git after |

Most of `.archeia/` is shape 1 (living). A smaller but essential subset is shape 2 (accumulating). A minority is shape 3 (transient), and it's concentrated in `execution/` and a few corners of `business/` and `growth/`.

The rest of this document specifies each shape in detail and maps the kernel operations onto them.

---

## 2. Shape 1: Living documents

### Definition

A living document is a single file that represents one concept. It is edited in place as the concept evolves. The file always contains the current truth about what it describes. History lives in git — `git log <path>` shows every version, `git show <commit>:<path>` retrieves any past state.

### Examples by domain

- **`product/`** — `product.md`, files under `design/`
- **`codebase/`** — `architecture/architecture.md`, `architecture/system.json`, `architecture/containers.json`, `architecture/components.json`, `architecture/dataflow.json`, `architecture/entities.json`, `architecture/statemachine.json`, `standards/standards.md`, `guide.md`, `scan-report.md`, `git-report.md`, everything under `diagrams/`
- **`business/`** — `vision/vision.md`, `strategy/strategy.md`
- **`growth/`** — `metrics/current.md` and any ongoing dashboard-style summaries

### Rules

1. **One file per concept.** There is one `product.md`, one `architecture.md`, one `vision.md`. Never `product-v1.md`, `product-v2.md`, `product-current.md`. The concept has a canonical path and that path is stable forever.
2. **Edit in place.** Updates are commits to the same file. No renames, no suffix games, no supersession chains.
3. **No `temporal_state` field.** Living documents are implicitly "always present." Frontmatter can have whatever a distribution needs (`title`, `updated_at`, `owner`), but temporal state is not a meaningful question for them.
4. **No supersession.** There is nothing to supersede — there's only the current version and git history.
5. **No pruning.** Living documents are never deleted under normal operation. They're core project knowledge.

### Typical frontmatter

```yaml
---
title: Product Spec
owner: product
updated_at: 2026-04-12T15:30:00Z
---
```

That's the whole frontmatter. No `status`, no `temporal_state`, no supersession links. The file is the file. Git holds history.

### Why this is right

Nobody versions a product spec as separate files. You edit the spec. You commit. You edit again. That's how humans already work on docs, and trying to impose past/present/future state on top of that is fighting the tool (git) that already solved the problem.

The living-document shape captures the majority of `.archeia/` because most project knowledge is this: the current state of a thing, evolved over time, with history preserved by the version control system you're already using.

---

## 3. Shape 2: Accumulating records

### Definition

An accumulating record is an append-only artifact. Each record has its own file and its own identity. Writing a new record does not replace the old one — both coexist on disk, with a `status` field indicating which is active. Records are *never deleted*. The entire history of decisions and authored events is directly readable in the filesystem.

### Examples by domain

- **`product/decisions/`** — ADRs. The canonical example. Each decision is its own file, written once, referenced forever. Supersession writes a new ADR that links to the old one; both stay.
- **`execution/retros/`** — retrospectives. Each retro is a record of a past event. They never get deleted because later work references them.
- **`business/landscape/`** — dated market research snapshots. Each snapshot is its own record. Old snapshots inform later strategy and stay on disk.
- **`growth/experiments/`** — concluded experiments *with their learnings*. Once an experiment ends, its file stays forever as a learning record. The raw running state of the experiment is different — that's shape 3 — but the concluded form with outcomes is shape 2.
- **`growth/channels/`** (retired channels) — retired channels with their performance history.

### Rules

1. **Each record has its own file and its own identity.** A new ADR is a new file (`decisions/20260412-1530-auth-rewrite.md`). Never edit an existing ADR to change its content (other than the single permitted mutation in rule 4).
2. **Append-only.** The set of records can grow; it cannot shrink. Records are never deleted.
3. **`status` field tracks relevance.** Common values: `active`, `superseded`, `archived`, `retired`. Semantics depend on the domain.
4. **Supersession is a write, not an edit.** To supersede record A with record B: write B with frontmatter `supersedes: <path-to-A>`, then do the *single permitted mutation* on A — update its frontmatter `status` from `active` to `superseded` and add `superseded_by: <path-to-B>`. No other edits to A are permitted. Both files stay on disk.
5. **No `temporal_state` field.** Time is not the axis here. The entire history of records is visible at once in the directory; readers filter by `status`, not by time.
6. **No pruning.** Ever. Accumulating records are the project's memory.

### Typical frontmatter

```yaml
---
title: Use PostgreSQL row-level security for multi-tenant isolation
created: 2026-04-12T15:30:00Z
author: architect
status: active
supersedes: null
superseded_by: null
---
```

And after supersession:

```yaml
---
title: Use PostgreSQL row-level security for multi-tenant isolation
created: 2026-04-12T15:30:00Z
author: architect
status: superseded
superseded_by: decisions/20260801-0900-schema-per-tenant.md
---
```

### Why this is right

The entire point of an ADR is that it stays forever. You don't prune a superseded decision — you write a new one that explains why the old one was wrong, and both live together so future readers can understand the reasoning. Retros are the same: you write a retro once, and later work references it to avoid repeating mistakes.

These artifacts are *authored history*. The act of writing them is the point. Treating them as transient is a category error.

Accumulating records look like a special case, but they're load-bearing: the entire design of an agentic workspace depends on having a way to capture decisions and events that other agents can read later without digging through git log archaeology.

---

## 4. Shape 3: Transient artifacts

### Definition

A transient artifact has a real lifecycle. It is created as a proposal, becomes active, reaches completion, and then — after a bounded retention window — gets pruned from the filesystem. Git preserves the long tail.

This is the only shape where temporal state (`future` / `present` / `past`) is a meaningful concept, and even here it's derived from a status field rather than stored separately.

### Examples by domain

- **`execution/tasks/`** — the canonical transient. A task is created as `todo`, becomes `active` when work starts, becomes `done` when work completes, and gets pruned from the filesystem after a retention window (default 14 days in Archeia Solo). Git preserves every state forever.
- **`execution/plans/`** — sprint plans. Active during a sprint, then superseded by the next sprint's plan and pruned after a retention window (default 30 days).
- **`business/drafts/`** — draft proposals. Either advance into a living document (draft becomes part of `vision.md` or `product.md` and the draft is deleted) or are discarded outright (retention window 0 — pruned on rejection).
- **`growth/experiments/` (running only)** — an experiment's running state is transient. Once it concludes, it either gets promoted to an accumulating record (shape 2) with its outcome, or — if no learning is worth keeping — it's pruned entirely.

### Rules

1. **Has a `status` field.** Status values are distribution-defined per artifact type. Typical for tasks: `todo`, `active`, `done`, `cancelled`. Typical for drafts: `draft`, `review`, `advanced`, `discarded`.
2. **Temporal state is derived from status.** There is no `temporal_state` field in the frontmatter. The distribution defines a mapping from each status value to a temporal category (future / present / past). Readers who care about temporal state look up the mapping, don't read a field.
3. **Has a retention window.** The distribution defines how long a transient artifact stays on disk after reaching a terminal status. Archeia Solo defaults: tasks 14 days, plans 30 days, discarded drafts 0 days.
4. **Has a terminal timestamp.** When an artifact reaches a terminal status (`done`, `cancelled`, `advanced`, `discarded`), a timestamp is recorded in frontmatter (e.g., `completed_at: 2026-04-12T16:45:00Z`). The retention window starts ticking from this timestamp.
5. **Pruned when the window expires.** A maintenance operation (e.g., `archeia:prune`) walks transient artifacts, checks retention windows, and deletes expired ones. Git preserves the file forever.
6. **Supersession is rare.** Transient artifacts usually don't supersede — they complete and get pruned. If supersession is genuinely needed, promote the artifact to shape 2 (accumulating) first.

### Typical frontmatter

```yaml
---
id: 2.3
title: Rewrite auth middleware
created: 2026-04-12T10:00:00Z
started: 2026-04-12T14:30:00Z
completed: 2026-04-13T16:45:00Z
status: done
scope:
  - server/auth/**
acceptance_criteria:
  - JWT refresh token flow works end-to-end
  - All existing auth tests pass
---
```

No `temporal_state`. The `status: done` plus the `completed` timestamp is enough — temporal state is `past`, retention window starts at 2026-04-13T16:45:00Z, and the file is eligible for pruning after that date + the distribution's retention setting.

### Why this is right

Tasks are the one thing that genuinely has a lifecycle worth tracking. They're born proposed, they do work, they finish. Keeping done tasks on disk forever is noise — after a sprint or two, they're just context clutter. But deleting them immediately loses the "what did we just ship?" signal that's useful in the next session.

Retention windows solve this: keep recent history on disk (glob-accessible, zero-latency) for the period when it's still operationally relevant, then delete and let git hold the archive. This is the correct lifecycle model because it matches how humans actually treat task state — recent matters, ancient doesn't, and git is the ancient archive.

---

## 5. The status → temporal mapping

Transient artifacts don't store temporal state; they store status, and temporal state is derived by the distribution's mapping table. Here's Archeia Solo's default mapping:

| Artifact type | Status | Temporal |
|---|---|---|
| Task | `todo`, `backlog` | `future` |
| Task | `active`, `in_progress`, `review` | `present` |
| Task | `done`, `cancelled` | `past` |
| Plan | `proposed` | `future` |
| Plan | `current` | `present` |
| Plan | `superseded` | `past` |
| Draft | `draft`, `review` | `future` |
| Draft | `advanced` (merged into living doc), `discarded` | `past` |
| Running experiment | `proposed` | `future` |
| Running experiment | `running` | `present` |
| Running experiment | `concluded` | `past` |

A distribution is free to change the status vocabulary or the mapping. The standard requires only that the mapping exists and is documented in the distribution's spec.

---

## 6. The five kernel operations (mapped to shapes)

| Operation | Shape 1 (living) | Shape 2 (accumulating) | Shape 3 (transient) |
|---|---|---|---|
| **`advance`** | N/A | N/A | Promote status from a `future` value to a `present` value. E.g., task `todo` → `active`. |
| **`complete`** | N/A | N/A | Promote status from a `present` value to a `past` value. Record a terminal timestamp. Start retention clock. |
| **`prune`** | Never | Never | Delete an artifact whose retention window has expired. Git preserves. |
| **`supersede`** | N/A (edit in place) | Write new record with `supersedes:`, update old record's `status` to `superseded` | Rare; if genuinely needed, promote to shape 2 first |
| **`evolve`** | `git log <path>` — walk commit history | Walk `supersedes:` / `superseded_by:` chain on disk | Walk recent past-state artifacts on disk, then fall back to git log |

The operations are **owner-performed**, per Truth #4 in [PRINCIPLES.md](PRINCIPLES.md#4-ownership-plus-delegation-is-the-concurrency-model). Subagents may compute which transitions to make, but the owner always commits the frontmatter change, the git commit, or the file deletion.

---

## 7. The five domains × three shapes

| Domain | Living | Accumulating | Transient |
|---|---|---|---|
| **`business/`** | `vision/vision.md`, `strategy/strategy.md` | `landscape/*.md` | `drafts/*.md` |
| **`product/`** | `product.md`, `design/*.md` | `decisions/*.md` | (none) |
| **`codebase/`** | `architecture/*`, `standards/*`, `guide.md`, `scan-report.md`, `git-report.md`, `diagrams/*` | (none in the canonical layout) | (none) |
| **`growth/`** | `metrics/current.md` | `experiments/*.md` (concluded, with learnings), `channels/*.md` (retired) | `experiments/*.md` (running), `channels/*.md` (active) |
| **`execution/`** | (none — execution is all action, no living summary doc) | `retros/*.md` | `tasks/*.md`, `plans/*.md`, `projects/*.md` |

A few observations that fall out:

- **`codebase/` is purely living documents.** No accumulation, no transience. All of it is one-file-per-concept, edited in place, history in git.
- **`product/` has no transient state at all.** Product spec evolves (living), decisions accumulate (ADRs), and that's it. Drafts proposing product changes live in `business/drafts/`, not `product/`.
- **`execution/` is the only domain with heavy transient presence.** Tasks, plans, projects — these are the things that flow.
- **`growth/` has all three shapes.** Current metrics are living, channel and experiment records are accumulating, running experiments are transient.

---

## 8. Codebase is purely living documents

> **Named principle (upgraded).** The `codebase/` domain contains only living documents. It has no accumulating records and no transient artifacts. Every file in `codebase/` is edited in place, and every version of every file is preserved by git.

The earlier framing said "codebase is a witness, not a planner" and pointed out that codebase has no `future` state. The three-shapes model upgrades this to a stronger claim: codebase is purely shape 1. It doesn't plan, it doesn't accumulate decisions (those live in `product/decisions/`), and it doesn't have tasks or drafts (those live in `execution/` and `business/`). It is the current observed state of the code, always, and nothing more.

This is the purest form of the "codebase is downstream" principle. Codebase reads its own source files, produces living docs, and commits them. Git provides all the history anyone needs. No accumulation, no transience, no lifecycle — just continuous regeneration of the current truth.

---

## 9. Retention windows

Retention windows are a distribution concern, not a kernel concern. The standard requires only that transient artifacts have a retention window defined *somewhere* in the distribution's spec; the kernel does not pick the values.

**Archeia Solo defaults:**

| Artifact type | Retention after terminal status | Rationale |
|---|---|---|
| Task | 14 days | Covers "what did we just ship?" context for the next sprint |
| Plan | 30 days | A sprint's worth of history, since plans are sprint-scale |
| Discarded draft | 0 days | If it's rejected, it's rejected — git holds it |
| Concluded running experiment (no learning worth keeping) | 7 days | Short grace period in case someone wants to read the raw state |
| Concluded running experiment (with learning) | Promoted to accumulating record; original pruned after 7 days | The learning outlives the experiment |

Other distributions will pick different values. A research-lab distribution might keep experiments for 90 days. A compliance-driven distribution might keep tasks for 7 years (to satisfy audit requirements) — in which case tasks are effectively accumulating, not transient, and the distribution should model them as shape 2 instead.

**Who runs the pruner:** an inherent kernel skill (e.g., `archeia:prune`) walks transient artifacts, reads terminal timestamps, compares against retention windows from the distribution config, and deletes expired files. Each file deletion is its own git commit so the history is a clean audit trail.

---

## 10. Worked examples

### A task (shape 3)

```markdown
# Created:
---
id: 2.3
title: Rewrite auth middleware
created: 2026-04-12T10:00:00Z
status: todo
scope: [server/auth/**]
---

# Work starts (archeia:work runs `advance`):
---
id: 2.3
title: Rewrite auth middleware
created: 2026-04-12T10:00:00Z
started: 2026-04-12T14:30:00Z
status: active
scope: [server/auth/**]
---

# Work completes (archeia:work runs `complete`):
---
id: 2.3
title: Rewrite auth middleware
created: 2026-04-12T10:00:00Z
started: 2026-04-12T14:30:00Z
completed: 2026-04-13T16:45:00Z
status: done
scope: [server/auth/**]
pr: https://github.com/Hugopeck/archeia/pull/42
---

# 14 days later (archeia:prune deletes the file):
# git rm execution/tasks/2.3-rewrite-auth.md
# git preserves the full history forever.
```

### A product spec (shape 1)

```markdown
# 2026-01-15: First version
---
title: Product Spec
updated_at: 2026-01-15T09:00:00Z
---

# Product Spec
...initial features, constraints, priorities...

# 2026-04-12: Spec has grown
---
title: Product Spec
updated_at: 2026-04-12T17:00:00Z
---

# Product Spec
...new features added, some edited, priorities reshuffled...
```

Same file. Same path. Edited in place. `git log product.md` shows every version. No superseded files cluttering the directory. The spec is a living document and the living document shape gets out of git's way.

### An ADR (shape 2)

```markdown
# 2026-01-15: Decision written
# File: product/decisions/20260115-0900-row-level-security.md
---
title: Use PostgreSQL row-level security for multi-tenant isolation
created: 2026-01-15T09:00:00Z
author: architect
status: active
supersedes: null
superseded_by: null
---

## Context
...

## Decision
Adopt Postgres RLS for tenant isolation.

## Consequences
...

## Alternatives considered
...

# 2026-08-01: Decision is revisited and superseded
# New file: product/decisions/20260801-0900-schema-per-tenant.md
---
title: Use schema-per-tenant for multi-tenant isolation
created: 2026-08-01T09:00:00Z
author: architect
status: active
supersedes: decisions/20260115-0900-row-level-security.md
superseded_by: null
---

## Context
The RLS approach from decision 20260115 hit scale limits at N tenants.
Schema-per-tenant gives us isolation + independent migration schedules.

## Decision
Migrate to schema-per-tenant.

## Consequences
...

# And the OLD file gets its one permitted frontmatter mutation:
# File: product/decisions/20260115-0900-row-level-security.md
---
title: Use PostgreSQL row-level security for multi-tenant isolation
created: 2026-01-15T09:00:00Z
author: architect
status: superseded
supersedes: null
superseded_by: decisions/20260801-0900-schema-per-tenant.md
---
# Body is unchanged.
```

Both files stay on disk forever. Future readers can follow the `supersedes` / `superseded_by` links in either direction to understand the full history of the isolation decision.

### A scan report (shape 1)

```markdown
# codebase/scan-report.md always has one file.
# Regeneration edits in place; git holds history.

# 2026-04-01 run:
---
title: Scan Report
generated: 2026-04-01T12:00:00Z
skill: archeia:scan-repo
---

# Scan Report
...LOC, deps, test coverage, README gaps...

# 2026-04-12 run (same file, new content):
---
title: Scan Report
generated: 2026-04-12T18:00:00Z
skill: archeia:scan-repo
---

# Scan Report
...LOC, deps, test coverage, README gaps... (updated numbers)
```

No `scan-report-2026-04-01.md` sitting next to the current one. No archive directory. Just one file, regenerated, with history in git. If someone wants to compare today's scan to last month's scan, they run `git show HEAD~30:codebase/scan-report.md`.

### A draft that advances (shape 3 → shape 1)

```markdown
# business/drafts/20260412-1030-onboarding-rewrite.md (shape 3):
---
id: onboarding-rewrite
title: Rewrite onboarding to reduce first-week churn
created: 2026-04-12T10:30:00Z
author: hugopeck
status: draft
---

# Onboarding rewrite proposal
...

# After review and decision to advance into business/vision/vision.md:
# 1. archeia:create-vision (or similar) edits business/vision/vision.md
#    in place to incorporate the draft's content — shape 1 edit.
# 2. The draft's status becomes 'advanced', retention window starts.
# 3. After 0 days (Solo's default for drafts), the draft file is pruned.
# 4. git preserves the draft forever.
```

The living document (`vision.md`) grows. The draft disappears from disk immediately. Git holds the draft's history in case anyone wants to see it.

---

## 11. Summary

The three-shapes model replaces the past/present/future framing from earlier drafts. It is more truthful, because it describes how Archeia artifacts actually work instead of imposing a uniform lifecycle on things that don't have one. It is more useful, because it keeps `.archeia/` scannable by pruning transient artifacts and storing living-doc history in git where it belongs. It is more opinionated, because it forces each artifact to declare its shape, which prevents drift into "everything accumulates forever."

The kernel recognizes three shapes. The kernel ships five operations (`advance`, `complete`, `prune`, `supersede`, `evolve`) and specifies which apply to which shape. Everything else — status vocabularies, retention windows, shape assignments for each artifact type — is a distribution concern.

What falls out is a standard that gets out of git's way for the 80% of artifacts that are living documents, gives ADRs and retros the permanent home they need, and handles operational state (tasks, drafts) with bounded retention that matches how humans already think about those artifacts.

This is the temporal model. What's novel is not the categories themselves — accountants had ledgers, software had live docs, every to-do list is transient — but the recognition that an agentic workspace needs all three, each with different rules, and that trying to collapse them into a single model breaks at least two of them.
