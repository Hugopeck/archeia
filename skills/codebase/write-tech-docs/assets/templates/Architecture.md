---
layer: 3
depends_on: none
required_evidence: package.json, pyproject.toml, Cargo.toml, go.mod, src/, lib/, app/, *.prisma, models.py, schema.graphql
validation: all-required-sections-present, all-claims-cite-evidence, no-marketing-language, all-cited-paths-exist
---

## Purpose

Architecture.md is the system-level map of the repository — the document a
new engineer reads on day one, and the one a coding agent checks before making
structural changes. It answers: what is this system, how is it put together,
and how does data move through it?

Everything here must be factual and evidence-backed. Every claim cites a file
path. If evidence is insufficient for a section, mark the gap honestly:
`<!-- INSUFFICIENT EVIDENCE: [what is missing] -->`

---

## Required Sections

These six sections appear in every Architecture.md. They build on each other:
start with how confident the documentation is, then what the project *is*,
how it's *structured*, how parts *relate*, how data *moves*, and how to
*work on it*.

### Documentation Confidence

**Always include. Must be the first section in generated output.**

This section reports evidence quality per section, so agents and humans know
which parts of this document to trust and which to verify. Confidence is
granular — a repo can have high-confidence System Overview and low-confidence
Module Boundaries.

Content must include:
- **Per-section confidence table:** one row per Required Section (excluding
  this one), with a confidence level and a short reason:
  - `high`: section has full evidence, all claims cite file paths
  - `medium`: section has partial evidence, some claims inferred or one gap
  - `low`: section lacks evidence, most claims are inferred or marked
    INSUFFICIENT EVIDENCE
- **Overall confidence:** derived from the per-section levels. Use the
  lowest level that applies to 2+ sections. If all sections are high, overall
  is high. If one section is low, overall is still medium (one outlier). If
  2+ sections are low, overall is low.
- **Agent guidance:** one sentence per low-confidence section telling agents
  what to do differently in that area. High-confidence sections need no
  guidance. Omit the guidance block entirely if overall is high.

**Format:**
```
| Section | Confidence | Reason |
|---------|------------|--------|
| System Overview | high | Manifest and framework identified from `[file]` |
| Topology | high | Topology inferred from directory structure and docker-compose |
| Module Boundaries | low | No clear sub-module separation — flat `src/` directory |
| Data Flow | medium | Primary flow traced, but middleware chain inferred |
| Build and Development | high | All commands found in manifest scripts |

**Overall: medium** (1 low, 1 medium, 3 high)

**Low-confidence guidance:**
- **Module Boundaries:** No detectable module separation. Do not assume
  internal boundaries — treat `src/` as a single unit until boundaries are
  established.
```

For repos with fragmented or unclear architecture, this section is where that
reality is surfaced honestly — per section, not as a blanket label. A repo
with excellent dependency management but no module boundaries should say
exactly that, not flatten both into "medium."

### System Overview

**Always include.** One paragraph that orients the reader — what this project
is and what technology powers it.

Content must include:
- Primary language and version (from manifest)
- Primary framework (from dependencies)
- What the system does in one sentence (from README or manifest description)

**Format:**
```
This is a [language] [type] built with [framework]. It [one-sentence purpose].

**Evidence:** `[manifest file]` ([key dependency versions]), `[config file]`
```

### Topology

**Always include.** The highest-level structural view — the shape of the
system before you look at any code.

Content must include:
- **Type:** monolith, modular monolith, microservices, serverless, library, CLI,
  or hybrid. Infer from: single vs multiple entry points, presence of
  `docker-compose.yml` with multiple services, workspace configs, deploy configs.
- **Primary areas:** top-level source directories and their roles
- **External systems:** databases, caches, message queues, third-party APIs
  (infer from dependencies and config files)

**Format:**
```
- **Type:** [topology type]
- **Primary areas:** `[dir1]/` ([role]), `[dir2]/` ([role])
- **External systems:** [system] (via `[dependency]` in `[manifest]`)

**Evidence:** [file paths]
```

### Module Boundaries

**Always include.** Now that we know the shape, this section maps the major
pieces and how they depend on each other.

| Module | Path | Responsibility | Dependencies |
|--------|------|---------------|-------------|
| [Name] | `[path]/` | [What it does] | [What it imports from] |

Infer from: directory structure, import/require statements in entry point files,
workspace configurations.

**Evidence:** directory listing, import patterns in sampled source files.

### Data Flow

**Always include.** This is where the architecture comes alive — a step-by-step
trace of how data moves through the system for the primary use case. Each row
is one interaction between two participants.

| Step | Source | Target | Message | Type | Protocol | Evidence |
|------|--------|--------|---------|------|----------|----------|
| 1 | End User | API Server | POST /tasks | sync | HTTPS | `src/routes/tasks.ts` |
| 2 | API Server | Task Service | createTask(data) | sync | function call | `src/routes/tasks.ts` |
| 3 | Task Service | PostgreSQL | INSERT task | sync | SQL | `src/services/taskService.ts` |
| 4 | Task Service | API Server | task record | response | function call | `src/services/taskService.ts` |
| 5 | API Server | End User | 201 Created | response | HTTPS | `src/routes/tasks.ts` |
| 6 | API Server | Background Worker | enqueue notification | async | Redis/BullMQ | `src/services/notifications.ts` |

Here's what each column means:
- **Source/Target:** participant names matching containers or components from
  the C4 model (System.json, Containers.json, Components.json)
- **Message:** the action label — HTTP verb + path, function name, SQL
  operation, or queue message type
- **Type:** `sync` (caller blocks for response) | `async` (fire-and-forget,
  queue, event) | `response` (return path of a prior sync call)
- **Protocol:** `HTTPS` | `SQL` | `gRPC` | `Redis` | `function call` |
  `WebSocket` | `message queue`

Infer from: route files, handler functions, service layer patterns, model/ORM
files, queue/worker definitions.

**Evidence:** import chains in source files, route definitions, queue configs.

### Build and Development

**Always include.** The practical section — how to actually build, run, and
develop the project day to day.

Content must include:
- **Package manager:** (from lockfile type)
- **Build command:** (from manifest scripts or Makefile)
- **Dev command:** (from manifest scripts or Makefile)
- **Test runner:** (from test config files or manifest scripts)
- **Task automation:** (Makefile, Justfile, Taskfile — if present)

**Evidence:** manifest scripts section, lockfile, task runner config.

---

## Conditional Sections

These sections appear only when evidence supports them. Not every project has
an API, a database schema, or state machines — include only what you can back
with real files.

### Deployment

**Include if** deployment config files exist (Dockerfile, fly.toml, vercel.json,
render.yaml, railway.json, CI/CD workflows with deploy steps).

Content: deployment target, container configuration, CI/CD pipeline summary.

### API Surface

**Include if** the project exposes an API (route files, OpenAPI spec, GraphQL
schema, CLI argument parser).

Content: list of endpoints/commands, request/response format, authentication
method (if detectable from middleware or config).

### Data Model

**Include if** ORM models or schema definition files are detected (Prisma
schema, Django models, SQLAlchemy declarative models, TypeORM entities,
database migration files with CREATE TABLE).

This section captures the domain's data structure — the entities that persist
and how they relate to each other.

Content must include:
- **ORM/Schema technology:** (from manifest dependencies or schema files)
- **Core entities:** table of primary domain entities (not join tables, audit
  logs, or migration-tracking tables — focus on what matters to the domain)

| Entity | Source File | Description | Key Fields |
|--------|------------|-------------|------------|
| [Name] | `[path]` | [What it represents] | [2-4 important fields with types] |

- **Key relationships:** list of primary relationships between entities with
  cardinality

**Format:**
```
- `User` 1→N `Task` (creates) — `src/models/task.ts`
- `Project` 1→N `Task` (contains) — `src/models/task.ts`
- `Task` N→1 `Status` (has) — `src/models/task.ts`
```

Infer from: schema files, model definitions, migration files. Read the actual
model/schema files — do not infer entities from directory names alone.

**Evidence:** schema file paths, model file paths.

### State Lifecycles

**Include if** explicit state machines or lifecycle enums are detected. Look
for these signals:
- State machine libraries in manifest (xstate, django-fsm, aasm, statechart)
- Enum/const fields named `status`, `state`, `phase`, `stage` in model files
- Transition methods or guards in source code

State lifecycles capture how key domain objects change over time — the valid
states and what triggers each transition. One entry per stateful entity.

**Format:**
```
**[Entity] lifecycle** (`[source file]`):
States: [state1] → [state2] → [state3] → [terminal]
Transitions:
- [state1] → [state2]: [trigger/event] — `[evidence file]`
- [state2] → [state3]: [trigger/event] — `[evidence file]`
- [state2] → [cancelled]: [trigger/event] — `[evidence file]`
```

Only include entities with 3+ states and explicit transitions. Do not infer
state machines from generic boolean fields (is_active, is_deleted). If
transitions cannot be traced to actual code, be honest about the gap:
`<!-- INSUFFICIENT EVIDENCE: transitions for [Entity] -->`.

**Evidence:** enum definitions, state machine configs, transition method files.

### Workspace Structure

**Include if** the project is a monorepo (packages/, apps/, workspace config
in manifest).

Content: table of packages/apps with their purpose and inter-dependencies.

### Change Notes

**Include if** any of the following are detectable:
- High-risk areas (files with complex logic, auth, payment, data migration)
- Stable areas (configuration, simple CRUD, static assets)

Content:
- **High-risk areas:** [paths and why]
- **Stable areas:** [paths and why]
- **Open questions:** deferred to DECISIONS.md

---

## Inference Signals

This table maps what you find in the repository to what you write in
Architecture.md. When signals conflict, follow the priority order:
**manifest content > file extensions > directory structure > README claims**.

| Evidence | Maps to section | Conclusion |
|----------|----------------|-----------|
| Manifest dependencies | System Overview, Topology | Language, framework, external systems |
| Directory structure (`src/`, `lib/`, `app/`) | Module Boundaries | Module layout and roles |
| Import statements in entry points | Data Flow, Module Boundaries | Dependency direction |
| Manifest scripts (build, dev, test) | Build and Development | Dev workflow |
| Lockfile type | Build and Development | Package manager |
| Dockerfile, deploy configs | Deployment | Deploy target and method |
| Route files, OpenAPI spec | API Surface | Endpoints and format |
| Workspace config (workspaces field) | Workspace Structure | Monorepo layout |
| `docker-compose.yml` services | Topology | External system dependencies |
| Test config files | Build and Development | Test runner and setup |
| Schema files (`*.prisma`, `models.py`, `schema.graphql`) | Data Model | Entity names, fields, relationships |
| ORM library in manifest (prisma, django, sqlalchemy, typeorm) | Data Model | ORM technology |
| State machine library in manifest (xstate, django-fsm, aasm) | State Lifecycles | State machine technology |
| Enum/status fields in models | State Lifecycles | Stateful entities |

---

## Quality Rubric

The self-validation pass checks these four criteria. If a generated
Architecture.md doesn't pass all of them, it needs another editing pass.

- **COMPLETENESS:** Every Required Section is present, including Documentation
  Confidence as the first section. Every table has at least one row. System
  Overview names the language and framework. Documentation Confidence level
  is consistent with the number of gaps found.
- **TRUTHFULNESS:** Every factual claim cites a file path in `**Evidence:**`
  format. No technologies are listed that weren't found in manifests or imports.
  All cited file paths exist in the repo (verified by Glob).
- **CONCISENESS:** No section exceeds 30 lines. No marketing language. No filler
  phrases like "leverages modern best practices" or "robust and scalable."
- **DETERMINISM:** Sections appear in the order listed above. Tables use the
  exact column headers specified. Evidence citations use consistent format.

---

## Anti-Patterns

These are examples of the kind of output this template is designed to prevent.
If you find yourself writing something similar, stop and ground it in evidence.

- `This project uses modern best practices for web development.`
  → No evidence, marketing language. Instead: `This is a Python 3.12 API built
  with FastAPI. Evidence: pyproject.toml`
- `The architecture follows clean, well-organized patterns.`
  → Vague, no file references. Instead: `Three-layer structure: routes
  (src/routes/) → services (src/services/) → models (src/models/). Evidence:
  src/ directory listing`
- `Technologies: React, Node.js, PostgreSQL, Redis, Docker, Kubernetes`
  → Listing technologies not found in manifests. Only list what evidence
  confirms.
- A Data Flow section that describes hypothetical flows not traceable to
  actual source files.
- A Module Boundaries table with modules inferred from general knowledge
  rather than actual directory structure.
