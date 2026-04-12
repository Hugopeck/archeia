# Archeia Standard

Archeia is a standard for organizing project knowledge inside software repositories. It defines a directory schema, ownership model, and contracts so that AI agents, human operators, and tools share a single source of truth — versioned with the code, colocated in every clone.

The standard is tool-agnostic. Any skill, agent, or CLI that follows the schema can read from and write to `.archeia/`. The reference implementation ships as a set of skills organized by domain.

## The Problem

Architecture knowledge lives in a senior dev's head. Product decisions live in Notion. Business strategy lives in a founder's pitch deck. Growth experiments live in a spreadsheet. Task state lives in Jira. None of it lives where agents can see it — next to the code.

AI agents compensate by reading file names, inferring structure, and guessing. They get the topology wrong because the topology was never written down in a place they could find. When agents do produce documentation, there's no standard for where it goes, who owns it, or what format it takes. Every project reinvents this from scratch.

Archeia solves this by defining a canonical location (`.archeia/`), a fixed set of domains (business, product, codebase, growth, execution), clear ownership per domain, and contracts for cross-domain reads.

## Design Principles

**In the repository.** Not a wiki, not a shared drive, not a URL that requires a separate login. In the repo, versioned with the code, visible in every clone. Agents don't need network access or API keys to read project context.

**Structured, not freeform.** Each domain has a defined set of documents with known schemas. Agents can rely on files being where the standard says they are. Humans can navigate without a guide.

**Descriptive and prescriptive are separated.** Codebase documentation describes what the code *is* — regenerated from evidence, always replaceable. Product and business documentation prescribes what we *want* — authored by humans, locked after review. These are fundamentally different kinds of knowledge and they live in different domains.

**Ownership is explicit.** Every file in `.archeia/` has exactly one owner — the skill or agent authorized to write it. Other skills may read it but never modify it. Conflicts are impossible by design.

**The standard comes first.** `.archeia/` is not a tool's output folder. It's a shared workspace that tools are guests in. The schema is the contract; tools conform to it.

---

## Directory Schema

```
.archeia/
│
├── SCHEMA.md                          # This file — the standard itself
│
├── business/                          # Why we're building, for whom, how we make money
│   ├── vision/                        # Vision artifacts and design briefs
│   │   └── *.md
│   ├── landscape/                     # Market research, competitors, alternatives
│   │   └── *.md
│   ├── strategy/                      # Positioning, business model, pricing
│   │   └── *.md
│   └── drafts/                        # Product-vision drafts (pre-review, pre-lock)
│       └── *.md
│
├── product/                           # What we're building (locked, implementation-ready)
│   ├── product.md                     # The locked product spec
│   ├── design/                        # UI specs, mockups, interaction patterns
│   │   └── *.md
│   └── decisions/                     # ADR-style product decisions with rationale
│       └── *.md
│
├── codebase/                          # What the code is right now (descriptive, regenerated)
│   ├── architecture/                  # C4 JSONs, Architecture.md
│   │   ├── architecture.md
│   │   ├── system.json                # C4 System Context
│   │   ├── containers.json            # C4 Container
│   │   └── components.json            # C4 Component
│   ├── standards/                     # Coding conventions, tech standards
│   │   └── standards.md
│   ├── diagrams/                      # Mermaid files rendered from structured data
│   │   └── *.mmd
│   ├── guide.md                       # Dev setup, commands, testing, deployment
│   ├── scan-report.md                 # LOC, dependencies, test coverage, README gaps
│   └── git-report.md                  # Contributors, bus factor, churn, velocity
│
├── growth/                            # How we acquire, retain, monetize
│   ├── channels/                      # Acquisition channels, experiments
│   │   └── *.md
│   └── metrics/                       # KPIs, funnels, benchmarks
│       └── *.md
│
└── execution/                         # What we're doing right now
    ├── projects/                      # Active projects
    │   └── *.md
    ├── tasks/                         # Task state
    │   └── *.md
    └── plans/                         # Plans and roadmaps
        └── *.md
```

---

## Domains

### business/

**Purpose:** Captures the holistic business vision — why this product exists, who it's for, how it makes money, and what the competitive landscape looks like. This is the upstream input to everything else.

**Contents:**

| Path | Description |
|---|---|
| `vision/*.md` | Vision artifacts. Each captures a product idea, feature direction, or strategic pivot as a structured brief: premise, target user, value proposition, alternatives considered, scope decision. |
| `landscape/*.md` | Market research. Competitors, adjacent products, existing solutions, whitespace analysis. Evidence-based — links and citations, not opinions. |
| `strategy/*.md` | Business model, positioning, pricing, go-to-market. The "how we make money" layer. |
| `drafts/*.md` | Product-vision drafts. These are proposals that have not yet been reviewed and locked. A draft is the input to the product review process. Once reviewed and approved, the result is written to `product/product.md`. Drafts are never deleted — they're the audit trail. |

**Owner:** Business skills (formerly hstack).

**Reads from:** Nothing. Business is the upstream origin.

**Read by:** Product skills (for review and spec generation), growth skills (for channel strategy).

---

### product/

**Purpose:** The locked, implementation-ready definition of what we're building. Everything in `product/` has been reviewed against codebase reality and design feasibility. Engineers and designer agents treat this as the source of truth for what to build.

**Contents:**

| Path | Description |
|---|---|
| `product.md` | The locked product spec. Features, requirements, constraints, acceptance criteria. This is the canonical "what are we building" document. Generated from `business/drafts/` after review. |
| `design/*.md` | UI specs, interaction patterns, component inventories, mockup references. The visual and interaction layer of the product. |
| `decisions/*.md` | Product decisions in ADR (Architecture Decision Record) format. Each captures a decision, the context, alternatives considered, and rationale. Append-only — decisions are never modified, only superseded. |

**Owner:** Product skills.

**Reads from:** `business/drafts/` (as input to review), `codebase/architecture/` (for feasibility validation).

**Read by:** Codebase skills (to align architecture with product intent), execution skills (to generate tasks from specs).

**The review flow:**

```
business/drafts/draft-*.md
        │
        ▼
  Product Review Agent
  reads draft + codebase/architecture/
  validates feasibility, resolves ambiguity
        │
        ▼
  product/product.md  (locked)
  product/decisions/   (rationale captured)
```

A draft in `business/drafts/` is a proposal. It becomes a locked spec in `product/product.md` only after an agent review process that cross-references the codebase for feasibility and design for coherence. The review agent reads from `codebase/` but never writes to it.

---

### codebase/

**Purpose:** Descriptive, evidence-based documentation of what the code is right now. Everything in `codebase/` is regenerable — you can delete it and rebuild from source. Every claim cites a file path. No human decisions live here; only observations.

**Contents:**

| Path | Description |
|---|---|
| `architecture/architecture.md` | Prose architecture document following C4 Model structure. System context, containers, components, interactions. |
| `architecture/system.json` | C4 System Context as structured JSON. External actors, system boundary, integrations. |
| `architecture/containers.json` | C4 Container diagram data. Services, databases, queues, their relationships. |
| `architecture/components.json` | C4 Component diagram data. Internal modules, their responsibilities and dependencies. |
| `standards/standards.md` | Coding conventions extracted from the codebase. Naming, file organization, error handling, testing patterns. Descriptive (what the code does), not prescriptive (what it should do). |
| `diagrams/*.mmd` | Mermaid diagrams rendered from C4 JSONs and other structured data. System context, container, component, and data flow diagrams. |
| `guide.md` | Developer setup guide. Prerequisites, install steps, dev commands, testing instructions, deployment. Extracted from actual config files. |
| `scan-report.md` | Quantitative scan. LOC by language, dependency counts, test coverage gaps, README gaps. Counts only, no interpretation. |
| `git-report.md` | Git history analysis. Contributors, bus factor, churn hotspots, collaboration density, velocity trends. |

**Owner:** Codebase skills (formerly archeia-the-tool's scan and doc pipeline).

**Reads from:** The codebase itself (source files, config, git history). Also reads `product/product.md` to contextualize architecture against intent.

**Read by:** Product skills (for feasibility validation), execution skills (for task context).

**Regeneration contract:** Every file in `codebase/` includes a generation timestamp and the skill version that produced it. Any file can be deleted and regenerated without data loss. Colocated READMEs in source directories (outside `.archeia/`) are also owned by codebase skills but follow their own placement rules.

---

### growth/

**Purpose:** How we acquire, retain, and monetize users. Growth is its own discipline — it reads from both business (strategy, pricing) and product (features, specs) but is subordinate to neither.

**Contents:**

| Path | Description |
|---|---|
| `channels/*.md` | Acquisition channels. Each file documents a channel: hypothesis, experiments run, results, current status. |
| `metrics/*.md` | KPIs, funnel definitions, benchmarks, cohort analyses. The quantitative backbone of growth. |

**Owner:** Growth skills (future).

**Reads from:** `business/strategy/` (for positioning and pricing context), `product/product.md` (for feature context).

**Read by:** Business skills (to inform strategy iteration).

---

### execution/

**Purpose:** What we're doing right now. Active projects, tasks, plans, and roadmaps. The operational state of the work.

**Contents:**

| Path | Description |
|---|---|
| `projects/*.md` | Active projects. Each file defines a project: goal, scope, status, links to relevant product specs and codebase components. |
| `tasks/*.md` | Task state. Individual units of work with status, assignee (human or agent), dependencies, and acceptance criteria. |
| `plans/*.md` | Plans and roadmaps. Sequenced work over time — sprints, milestones, quarterly plans. |

**Owner:** Execution skills (formerly Track).

**Reads from:** `product/product.md` (to generate tasks from specs), `codebase/` (for technical context when scoping work).

**Read by:** All domains may read execution state for status awareness.

---

## Ownership Model

Every file in `.archeia/` has exactly one owning domain. The owning domain's skills are the only ones authorized to create, modify, or delete files in that domain's directories.

| Domain | Owner | May read |
|---|---|---|
| `business/` | Business skills | — |
| `product/` | Product skills | `business/drafts/`, `codebase/architecture/` |
| `codebase/` | Codebase skills | Source code, git history, `product/product.md` |
| `growth/` | Growth skills | `business/strategy/`, `product/product.md` |
| `execution/` | Execution skills | `product/product.md`, `codebase/` |

**Rules:**

1. **Write to your domain only.** A business skill never writes to `product/`. A codebase skill never writes to `execution/`.
2. **Read across domains freely.** Any skill may read any file in `.archeia/` for context. The ownership rule governs writes, not reads.
3. **No implicit writes.** A skill that reads `business/drafts/` to produce `product/product.md` is doing a cross-domain read followed by a same-domain write. The read is from `business/`; the write is to `product/`. This is correct behavior.
4. **Schema enforcement.** Each domain defines the expected files, naming conventions, and frontmatter schema. Skills validate before writing.

---

## Cross-Domain Contracts

When a skill in one domain reads from another, it depends on a contract — the format and location of the file it's reading. These contracts are the interfaces between domains.

### business → product

**File:** `business/drafts/*.md`

**Contract:** Each draft must include YAML frontmatter with:

```yaml
---
title: string           # working title
status: draft | review | locked | superseded
created: ISO 8601 date
author: string           # human or agent identifier
supersedes: filename     # optional, if this replaces a previous draft
---
```

The body is freeform Markdown but should cover: premise, target user, value proposition, scope, and alternatives considered.

Product skills read drafts with `status: review` and produce `product/product.md`.

### product → execution

**File:** `product/product.md`

**Contract:** The locked spec must include structured sections that execution skills can parse to generate tasks:

- **Features:** Each feature has a name, description, and acceptance criteria.
- **Constraints:** Technical and business constraints that scope the work.
- **Priorities:** Ordered list or MoSCoW classification.

Execution skills read the spec and generate `execution/projects/` and `execution/tasks/` entries.

### codebase → product

**File:** `codebase/architecture/architecture.md`, `codebase/architecture/*.json`

**Contract:** C4 JSON files follow the structured schema:

```json
{
  "level": "system | container | component",
  "elements": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "technology": "string",
      "relationships": [
        {
          "target": "element_id",
          "description": "string",
          "technology": "string"
        }
      ]
    }
  ]
}
```

Product skills read these during review to validate that a draft is feasible given the current architecture.

---

## Colocated Files

Some files live outside `.archeia/` but are owned by Archeia skills:

| File | Location | Owner | Purpose |
|---|---|---|---|
| `AGENTS.md` | Repo root | Codebase skills | Cross-platform agent instructions (agents.md standard) |
| `CLAUDE.md` | Repo root | Codebase skills | Claude Code-specific instructions |
| `README.md` | Per directory | Codebase skills | Directory-level context, key concepts, learnings |
| `agents.md` | Per directory | Codebase skills | Local agent rules where they differ from root |

These follow the same ownership rules — codebase skills own them, other skills read them.

---

## Reference Implementation

The reference implementation is a single repository containing skills organized by domain:

```
archeia/
├── standard/                          # The spec (this document, schemas, contracts)
│   ├── SCHEMA.md
│   └── contracts/
│       └── *.md
│
├── skills/
│   ├── business/                      # Vision, landscape, strategy skills
│   │   ├── create-vision/
│   │   ├── research-landscape/
│   │   └── define-strategy/
│   │
│   ├── product/                       # Review, lock, design skills
│   │   ├── review-draft/
│   │   ├── lock-spec/
│   │   └── define-design/
│   │
│   ├── codebase/                      # Scan, document, diagram skills
│   │   ├── scan-repo/
│   │   ├── scan-git/
│   │   ├── write-architecture/
│   │   ├── write-readmes/
│   │   ├── write-agent-docs/
│   │   └── draw-diagrams/
│   │
│   ├── growth/                        # Channel, metrics skills (future)
│   │   └── ...
│   │
│   └── execution/                     # Project, task, plan skills
│       ├── create-project/
│       ├── create-task/
│       └── create-plan/
│
├── install.sh                         # Install all skills
└── README.md
```

Each skill is a directory containing a `SKILL.md` and optional assets. Skills activate automatically when an agent detects a matching context.

### Installation

```bash
git clone https://github.com/hugopeck/archeia.git ~/.local/share/agent-skills/archeia
~/.local/share/agent-skills/archeia/install.sh
```

Or tell your agent:

> Install Archeia: clone `https://github.com/hugopeck/archeia.git` to `~/.local/share/agent-skills/archeia`, then run the install script.

### Running the Pipeline

Skills can run independently or in sequence. The full pipeline:

```
# Understand the business
/archeia:create-vision
/archeia:research-landscape
/archeia:define-strategy

# Understand the code
/archeia:scan-repo
/archeia:scan-git
/archeia:write-architecture
/archeia:write-readmes
/archeia:write-agent-docs
/archeia:draw-diagrams

# Lock the product
/archeia:review-draft
/archeia:lock-spec
/archeia:define-design

# Plan the work
/archeia:create-project
/archeia:create-task
/archeia:create-plan
```

Not every project needs every skill. A solo dev might only use codebase and execution. A product team might use all five domains.

---

## Built On

Archeia applies established methodologies and automates them:

- **[C4 Model](https://c4model.com/)** — Three-level architecture zoom (System, Container, Component) as structured JSON driving all diagrams and architecture docs.
- **[arc42](https://arc42.org/overview)** — Architecture documentation template informing the structure of `architecture.md`.
- **[Diataxis](https://docs.diataxis.fr/)** — Separates reference, how-to, explanation, and tutorial into distinct documents.
- **[Docs as Code](https://www.docops.io/docs-as-code/)** — Documentation lives in the repo, versioned with code, reviewed in PRs.
- **[agents.md](https://www.agents.md/)** — Open standard for agent-readable documentation. Archeia generates colocated rule files that any agent can read.
- **[ADR (Architecture Decision Records)](https://adr.github.io/)** — Lightweight decision capture format used in `product/decisions/`.

---

## FAQ

**Why `.archeia/` and not `.context/` or `.docs/`?**
Archeia means "archives" in Greek — a place where authoritative records are kept. The name signals intent: this is the canonical knowledge store, not a generic docs folder. The dot prefix keeps it out of the way in file explorers while remaining visible to agents.

**Can I use only some domains?**
Yes. Each domain is independent. A project might only have `codebase/` and `execution/`. The schema defines what *can* exist, not what must.

**What if I use a different project management tool?**
`execution/` is the Archeia-native format. If you use Jira, Linear, or another tool, execution skills can sync state between `.archeia/execution/` and the external tool, or you can skip `execution/` entirely. The other domains still work.

**How do colocated READMEs relate to `.archeia/`?**
Colocated READMEs (in source directories) are directory-level context. `.archeia/codebase/` is system-level context. They complement each other — READMEs explain "what this folder does," while `codebase/architecture/` explains "how the system fits together." Both are owned by codebase skills.

**Can multiple agents write to the same domain?**
Multiple agents can write to the same domain if they're all running the same domain's skills. The ownership rule is per-domain, not per-agent. Two codebase agents can both write to `codebase/` — they're using the same skills and following the same schema. What's prohibited is a business agent writing to `codebase/`.

**Is `.archeia/` committed to git?**
Yes. The entire point is that architecture knowledge is versioned with the code. Regenerable files (like `scan-report.md`) can be `.gitignored` if you prefer to regenerate on CI, but the default is to commit everything.

---

## License

The Archeia Standard is released under the MIT License.
