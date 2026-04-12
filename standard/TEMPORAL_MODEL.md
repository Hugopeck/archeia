# The Temporal Model

> **Claim:** every artifact in `.archeia/` refers to a moment. That moment — past, present, or future — is a first-class field, not an afterthought. Transitions between states are kernel operations. History is a native query, not a git archaeology exercise.

This document specifies the temporal model that underlies the Archeia Standard. It is the single most original contribution in the kernel, and the one that has to be internalized before the rest of the standard makes sense.

---

## 1. The three states

Every artifact in every domain is in one of exactly three temporal states. The field is recorded in YAML frontmatter as `temporal_state`.

| State | Meaning | Typical content |
|---|---|---|
| **`past`** | This artifact describes something that has happened, been done, or been superseded. Read for history and evidence, never modified in place. | Retrospectives, git-history analyses, completed tasks, archived projects, superseded product specs, retired strategies, completed growth experiments. |
| **`present`** | This artifact describes what is true, committed, or in force right now. This is the working state. | Current architecture, locked product spec, active task, in-progress plan, current growth channels, current business strategy. |
| **`future`** | This artifact describes what is intended, proposed, planned, or desired — but not yet committed. | Draft vision, proposed decisions, todo tasks, backlog projects, channel hypotheses, upcoming strategy shifts. |

The temporal state is **per artifact**, not per domain. A single domain can hold artifacts in all three states at once — the `business/` domain typically has past strategies, a current vision, and future drafts side by side.

---

## 2. Metadata, not directories

The standard specifies the temporal model as **frontmatter metadata**, not as directory structure.

A canonical artifact looks like:

```markdown
---
title: Auth Rewrite Vision
temporal_state: future
created: 2026-04-12T10:30:00Z
author: hugopeck
status: draft
---

# Auth Rewrite Vision

...
```

Filtering artifacts by temporal state is a frontmatter grep — agents and tools use a glob over the domain directory and a filter on the `temporal_state` field.

### Why metadata over directories

There are two plausible layouts. The standard commits to metadata-only for three reasons:

1. **Transitions are updates, not moves.** When a draft is locked, its `temporal_state` changes from `future` to `present`. With metadata, that's a single frontmatter edit. With directories, it's a file move — which breaks any link pointing at the old path, pollutes git history with renames, and forces every link in every other artifact to be rewritten.

2. **One artifact, one path, one identity.** A task that lives at `.archeia/execution/tasks/2.3-rewrite-auth.md` keeps that path for its entire life, from the moment it's created as a future todo to the moment it's archived as a past done-task. Its identity is stable; only its temporal state changes.

3. **Distributions stay flat.** Forcing every domain to have `past/`, `present/`, `future/` subdirectories imposes a tree shape on distributions that may not want one. Archeia Solo wants `execution/tasks/` to be flat (that's how track did it). Metadata-only gives distributions the freedom to organize their trees by concept rather than by time.

Distributions are free to adopt directory-based layouts internally if they prefer — nothing in the standard forbids `execution/tasks/past/` as a convention in a specific distribution. But the **standard** specifies temporal state as a frontmatter field, and conforming tools read that field first.

---

## 3. The three kernel operations

The temporal model defines three kernel operations — one for each transition and one for history traversal. These are inherent skills of the standard and every conforming distribution must implement or delegate to them.

Every operation is **performed by the domain owner**, not by arbitrary agents. The owner may delegate the *work* of computing a transition (e.g., "which tasks should move from future to present in this sprint?") to subagents via the concurrency model in [Truth #4 of PRINCIPLES.md](PRINCIPLES.md#4-ownership-plus-delegation-is-the-concurrency-model), but the *commit* of the new frontmatter state is always the owner's write. Subagents compute; the owner commits.

### `advance` — future → present

An artifact in the `future` state becomes the present state of its concept. This is the "commitment" operation.

- A `future` draft under `product/` is reviewed and locked: its `temporal_state` changes to `present`, its `status` changes to `locked`, and a timestamp is recorded.
- A `future` todo task in `execution/` becomes active: `temporal_state: present`, `status: active`.
- A `future` channel hypothesis in `growth/` is greenlit as a running experiment: `temporal_state: present`.

Advance is **idempotent on already-present artifacts** — calling it on something already present is a no-op. It is **non-destructive** — the previous state's metadata (when it was created, who authored it, what preceded it) is preserved in the frontmatter history.

### `archive` — present → past

An artifact in the `present` state is retired. Its concept has been completed, superseded, or deprecated.

- A `present` task in `execution/` completes successfully: `temporal_state: past`, `status: done`.
- A `present` product spec is superseded by a newer one: `temporal_state: past`, `status: superseded`, `superseded_by:` field points at the new spec.
- A `present` growth channel is retired: `temporal_state: past`, `status: retired`.

Archive **never deletes**. The file stays exactly where it is, its temporal state flips, and any readers filtering for `temporal_state: past` now see it. History is preserved by doing nothing — no moves, no copies, no separate archive tree.

**Supersession is archive with a successor.** When an artifact is superseded, archive the old one and create a new `present` or `future` artifact that references it via `supersedes:` frontmatter. The old artifact gets `superseded_by:` pointing at the new one. A bidirectional link, preserved forever.

### `evolve` — walk the past chain

Given a concept, walk its history by following `supersedes:` / `superseded_by:` links backwards through `past`-state artifacts. The result is a timeline of how the concept changed, who authored each version, when, and why.

This is the kernel's native answer to "how did we end up here?" It replaces archaeological git log spelunking with a frontmatter graph traversal. Every distribution that implements `advance` and `archive` gets `evolve` for free.

---

## 4. The five domains × three states

Here's what past, present, and future mean in each canonical software domain.

### `business/`

| State | Contents |
|---|---|
| **past** | Retired strategies, superseded vision docs, archived landscape snapshots, closed market research |
| **present** | Current strategy, current vision, active landscape analysis |
| **future** | Proposed drafts, upcoming strategy shifts, hypothetical market expansions |

### `product/`

| State | Contents |
|---|---|
| **past** | Superseded `product.md` versions, retired decisions, obsolete designs |
| **present** | Current locked `product.md`, current design specs, active decisions |
| **future** | Draft decisions under review, proposed features, design explorations |

### `codebase/`

| State | Contents |
|---|---|
| **past** | Historical git-reports, old scan-reports, architecture snapshots from prior releases |
| **present** | Current `architecture.md`, current standards, current guide, current scan-report, current diagrams |
| **future** | **Empty. Codebase has no future.** See §5 below. |

### `growth/`

| State | Contents |
|---|---|
| **past** | Completed experiments with results, retired channels, archived metrics reports |
| **present** | Active channels, current metrics, running experiments |
| **future** | Proposed experiments, channel hypotheses, planned funnel changes |

### `execution/`

| State | Contents |
|---|---|
| **past** | Done tasks, completed projects, retrospectives, closed plans |
| **present** | Active task, in-progress plan, current sprint state |
| **future** | Todo tasks, backlog projects, upcoming sprints |

Every domain except one uses all three states. The exception is `codebase/`, and that exception is a principle.

---

## 5. Codebase is a witness, not a planner

> **Named principle.** The `codebase/` domain has no `future` state. Every artifact in `codebase/` has `temporal_state: present` or `temporal_state: past`.

`codebase/` is observational. Its job is to answer "what IS the code right now?" and "what WAS the code at previous snapshots?" It never answers "what SHOULD the code be?" — that question belongs to a different domain.

Where planned code changes live:

- **Product intent** → `product/` (future, present, past decisions and specs)
- **Task breakdown** → `execution/` (future todos, present active work, past done tasks)
- **Growth experiments requiring code** → `growth/` (future hypotheses, present running experiments)

When a codebase skill is asked to regenerate `codebase/present/architecture.md`, it reads the actual source files — not some future-state plan. The codebase domain is always downstream, always a report, always grounded in evidence you can point at with `cat`.

This asymmetry is deliberate and load-bearing. It enforces the **forward flow** that the rest of the standard depends on, described in the next section.

---

## 6. The forward flow: product → execution → codebase

The canonical causal direction of work in Archeia is:

```
business  →  product  →  execution  →  codebase
                    ↘
                     →  growth
```

**Business** declares why we're building. **Product** turns that into what we've committed to build. **Execution** turns product intent into the actual work of building. **Codebase** is the resulting system, observed. **Growth** forks off from product in parallel — it turns product intent into customer-facing acquisition and retention experiments.

Work flows forward. Each stage reads from its upstream and writes its own domain:

- Business reads nothing (it's the origin) and writes `business/`
- Product reads `business/` and writes `product/`
- Execution reads `product/` and writes `execution/`
- Codebase reads the actual code and writes `codebase/` (evidence-based; `product/` is consulted for context but never dictates)
- Growth reads `business/` and `product/` and writes `growth/`

The forward flow is what makes the "codebase has no future" asymmetry principled. You don't plan code in `codebase/` because code plans flow *into* `codebase/` through execution. By the time a change lands in `codebase/present/`, it has already been a `future` product decision, a `present` product spec, a `future` execution task, a `present` execution task, and finally a `past` execution task that produced the code `codebase/` now observes.

## 7. The read flow: everyone reads codebase and product

The forward flow describes causation. The **read flow** describes where agents fetch context, and it goes in a different direction:

```
            ┌──── codebase (read by everyone for system context)
            │
            │         ┌──── product (read by execution, growth, and
            │         │                codebase-for-framing)
            ▼         ▼
        agents in every domain
```

Everyone reads `codebase/` for system context. Everyone reads `product/` for intent. Nobody writes to them except their owners. This is consistent with the ownership-plus-delegation principle ([Truth #4 in PRINCIPLES.md](PRINCIPLES.md#4-ownership-plus-delegation-is-the-concurrency-model)): reads are free, writes are owner-only, and parallelism comes from the owner delegating to subagents rather than from concurrent access.

The read flow is why `codebase/` is so load-bearing. It's the single source of truth for "what exists right now in the system we're building," and every other domain's agents consult it to ground their decisions in reality.

---

## 8. Worked examples

### A task's journey (execution domain)

A task is created as a `future` todo, becomes the active `present` task when work starts, and archives to `past` when work completes.

```markdown
# When created (by archeia:create):
---
id: 2.3
title: Rewrite auth middleware
temporal_state: future
status: todo
created: 2026-04-12T10:00:00Z
---

# When work starts (archeia:work runs `advance`):
---
id: 2.3
title: Rewrite auth middleware
temporal_state: present
status: active
created: 2026-04-12T10:00:00Z
started: 2026-04-12T14:30:00Z
---

# When work completes (archeia:work runs `archive`):
---
id: 2.3
title: Rewrite auth middleware
temporal_state: past
status: done
created: 2026-04-12T10:00:00Z
started: 2026-04-12T14:30:00Z
completed: 2026-04-13T16:45:00Z
pr: https://github.com/Hugopeck/archeia/pull/42
---
```

Same file, same path, same identity. Only frontmatter changes.

### A product spec's supersession (product domain)

The current `product.md` is superseded by a newer version after an architectural pivot.

```markdown
# Old spec, archived:
---
title: Auth v1 spec
temporal_state: past
status: superseded
locked: 2026-01-15T09:00:00Z
superseded_by: product.md  # the new one
superseded_at: 2026-04-12T17:00:00Z
---

# New spec, current:
---
title: Auth v2 spec
temporal_state: present
status: locked
locked: 2026-04-12T17:00:00Z
supersedes: product-v1-2026-01-15.md
---
```

The old spec is renamed to `product-v1-2026-01-15.md` to free the canonical `product.md` path for the new current version. Both files stay under `product/`, and `evolve` can walk the `supersedes:` chain to show the history.

### A scan-report's life (codebase domain)

`codebase/scan-report.md` is always `present`. When the codebase scanner re-runs, the old scan-report is archived as `past` and a new `present` one takes its place.

```markdown
# Before regeneration:
---
title: Scan Report
temporal_state: present
generated: 2026-04-01T12:00:00Z
skill_version: 0.0.1
---

# After regeneration (old report archived):
---
title: Scan Report (2026-04-01)
temporal_state: past
generated: 2026-04-01T12:00:00Z
skill_version: 0.0.1
archived_at: 2026-04-12T18:00:00Z
superseded_by: scan-report.md
---

# And the new report:
---
title: Scan Report
temporal_state: present
generated: 2026-04-12T18:00:00Z
skill_version: 0.0.1
supersedes: scan-report-2026-04-01.md
---
```

`codebase/` is the exception that proves the rule: it has `past` and `present` but no `future`. Every regeneration is a supersession, and the past chain gives you the evolution of how the system has been understood over time.

### A growth experiment's life (growth domain)

A growth experiment starts as a `future` hypothesis, runs as a `present` active experiment, and archives to `past` with results.

```markdown
# Proposed:
---
title: Referral bonus experiment
temporal_state: future
status: hypothesis
---

# Running:
---
title: Referral bonus experiment
temporal_state: present
status: running
started: 2026-04-12T00:00:00Z
---

# Concluded:
---
title: Referral bonus experiment
temporal_state: past
status: concluded
started: 2026-04-12T00:00:00Z
concluded: 2026-04-26T00:00:00Z
outcome: -3% conversion, abandoned
---
```

The conclusion includes the result — the past-state artifact is now a learning the business strategy can read when deciding the next experiment.

---

## 9. Required frontmatter fields

Every conforming artifact in every domain MUST have:

```yaml
temporal_state: past | present | future
```

Every artifact SHOULD have:

```yaml
title: string
created: ISO 8601 datetime
author: string
```

Every artifact that has transitioned at least once SHOULD have:

```yaml
status: <domain-specific>        # e.g. draft, review, locked, active, done, superseded
```

Artifacts involved in supersession chains SHOULD have:

```yaml
supersedes: relative path to the predecessor (or null)
superseded_by: relative path to the successor (or null)
```

Domain-specific skills are free to add additional fields. The standard requires the above four; everything else is distribution or domain convention.

---

## 10. Summary

The temporal model adds one primitive (`temporal_state`), three operations (`advance`, `archive`, `evolve`), and one principled asymmetry (`codebase has no future`). From that foundation comes a native theory of project time: history, intent, and current state all live in the same tree, differentiated by a single frontmatter field.

It's the piece of the Archeia Standard that turns a static in-repo knowledge store into something that moves with the project — and gives agents a way to reason about when each claim applies without building a separate timeline system.
