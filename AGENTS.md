# AGENTS.md

This file provides guidance to AI coding agents working in this repository.

## What This Repo Is

Archeia is the reference implementation of the **Archeia Standard** — a standard for organizing project knowledge inside software repositories. The standard defines a canonical location (`.archeia/`), five domains (business, product, codebase, growth, execution), clear ownership per domain, and contracts for cross-domain reads.

The spec lives at [`standard/SCHEMA.md`](standard/SCHEMA.md). The reference implementation ships as a set of skills under `skills/`, organized by domain.

This is a monorepo that absorbed three previous projects:
- Former `archeia` (codebase domain) — now `skills/codebase/`
- Former `hstack` (product domain) — now `skills/product/`
- Former `track` (execution domain) — now `skills/execution/`

All skills install under the `archeia:` namespace — e.g. `archeia:scan-repo`, `archeia:work`, `archeia:clarify-idea`.

## Repo Layout

```
archeia/
├── standard/                # The spec
│   ├── SCHEMA.md            # The Archeia Standard
│   └── VERSION              # Semver for the standard
├── skills/
│   ├── business/            # (stubbed, future)
│   ├── product/             # Product-domain skills (formerly hstack)
│   ├── codebase/            # Codebase-domain skills (formerly archeia)
│   ├── growth/              # (stubbed, future)
│   └── execution/           # Execution-domain skills (formerly track)
├── evals/                   # Codebase-domain eval harness (Python)
├── docs/                    # Reference bibliography
└── install.sh               # Symlinks all skills into ~/.claude/skills/
```

## Skill Pipelines by Domain

### Codebase domain

Skills run in a fixed order against a **target repository**. Each reads artifacts produced by earlier skills:

1. **`archeia:scan-repo`** → `.archeia/codebase/scan-report.md` (quantitative metrics, README coverage gaps)
2. **`archeia:scan-git`** → `.archeia/codebase/git-report.md` (team dynamics, collaboration patterns)
3. **`archeia:write-tech-docs`** → `.archeia/codebase/architecture/architecture.md`, `system.json`, `.archeia/codebase/standards/standards.md`, `.archeia/codebase/guide.md`, root `AGENTS.md`/`CLAUDE.md`, plus always-attempted `containers.json`, `components.json`, `dataflow.json`, and conditional `entities.json` / `statemachine.json`
4. **`archeia:write-readmes`** → colocated `README.md` per directory (driven by scan-report coverage table)
5. **`archeia:write-agents-docs`** → colocated `agents.md` + `claude.md` pairs (only where local rules differ from root)
6. **`archeia:draw-diagrams`** → `.archeia/codebase/diagrams/` Mermaid files generated from the C4 JSONs

### Product domain (ported from hstack)

1. **`archeia:clarify-idea`** → `.archeia/business/drafts/*.md` — explore a rough idea, save a design brief
2. **`archeia:create-vision`** → `.archeia/business/vision/*.md` — pressure-test a plan and save a vision artifact
3. **`archeia:review-draft`** → `.archeia/product/product.md` (locked) — convert a `status: review` draft into the implementation-ready spec
4. **`archeia:lock-spec`** → `.archeia/product/decisions/*.md` — append an ADR-style decision record

### Execution domain (ported from track)

1. **`archeia:setup-track`** → scaffolds `.archeia/execution/` in an adopting repo (script installation is Phase 3+ — see SKILL.md migration note)
2. **`archeia:create`** → `.archeia/execution/projects/*.md` or `.archeia/execution/tasks/*.md` — create projects/tasks from natural language, reads `.archeia/product/product.md` when present
3. **`archeia:decompose`** → breaks a project brief into parallel task files
4. **`archeia:work`** → runs the active work session on a tracked task
5. **`archeia:todo`** → regenerates `BOARD.md` / `TODO.md` / `PROJECTS.md` views (requires the not-yet-ported `track-todo.sh`)
6. **`archeia:update-track`** → auto-update skills at session start

**Execution domain port note:** Only SKILL.md files, `work/references/`, and the four template readmes under `setup-track/assets/` were ported in Phase 2. The bash enforcement layer (`scripts/`, git hooks, GitHub Actions workflows, `install-manifest.json`, `track-ruleset.json`) stays in `github.com/Hugopeck/track` and can be selectively backported later. See the migration note at the top of each execution SKILL.md.

## Personal Subagents

The `agents/` folder at the repo root contains Claude Code **subagents** — role-shaped AI assistants (`architect`, `engineer`) that install to `~/.claude/agents/` and become available in every repo. They coexist with the domain skills under `skills/`: skills own workflows, agents own roles.

Each agent is Archeia-aware: its system prompt names the exact `.archeia/<domain>/` paths it reads and writes. When invoked in a repo without `.archeia/`, the agent falls back to generic code-reading behavior.

`install.sh` symlinks each `agents/*.md` (except the README) into `~/.claude/agents/<name>.md`. Symlinks mean a `git pull` here immediately updates the installed agents with no re-install step.

See `agents/README.md` for the install flow, invocation patterns, and how to add new agents.

## Cross-Domain Contracts

See `standard/SCHEMA.md` for the full ownership and read/write rules. The three contracts that span domains:

- `business/drafts/*.md` → `product/product.md` (YAML frontmatter contract)
- `product/product.md` → `execution/` (Features, Constraints, Priorities sections drive task creation)
- `codebase/architecture/*.json` → `product/` (C4 JSON schema informs feasibility review)

## How to Work on Skills

Each skill lives in `skills/<domain>/<skill-name>/`:

```
skills/<domain>/<skill-name>/
  SKILL.md              The skill prompt (YAML frontmatter + workflow)
  README.md             What the skill does (for humans browsing the repo)
  references/           Protocol docs, examples (rationale, not instructions)
  assets/templates/     Output or transformation exemplars
  scripts/              Helper scripts (where applicable)
  evals/                Per-skill eval configs
```

When modifying a skill's behavior, change `SKILL.md`. When changing what the skill produces, update the relevant template in `assets/templates/` and the protocol in `references/`. Keep them in sync.

## Validation Scripts (codebase domain)

Run from this repo against a target repo:

```bash
# Generate exploration plan for a target repo
bash skills/codebase/write-tech-docs/scripts/discover.sh /path/to/target-repo

# Validate evidence citations in generated .archeia/codebase/ docs
bash skills/codebase/write-tech-docs/scripts/validate-evidence.sh /path/to/target-repo

# Collect git history data (run from target repo)
bash /path/to/archeia/skills/codebase/scan-git/scripts/git-scanner.sh
```

## Evidence Principle (codebase domain)

The non-negotiable rule for codebase skills: every factual claim in generated docs must cite a file path from the target repo. No claims from general knowledge. Insufficient evidence is marked with `<!-- INSUFFICIENT EVIDENCE: [what is missing] -->` — never fabricated.

## Output Dispositions

The codebase domain uses three output dispositions:

- **Always generated** — the file is written on every run; gaps are recorded inside the file
- **Always attempted** — the template is evaluated on every run, but the file is skipped with an explicit insufficiency outcome if the required structure cannot be evidenced
- **Conditional** — generation is attempted only when a triggering evidence class exists

When working on `archeia:write-tech-docs` or downstream consumers like `archeia:draw-diagrams`, preserve this distinction. Missing always-attempted artifacts like `containers.json`, `components.json`, or `dataflow.json` can be valid outcomes and must not be treated as failures or fabricated downstream.

## Ownership Rules

Every file under `.archeia/` has exactly one owning domain. Skills write only to their own domain and read across domains freely. See `standard/SCHEMA.md` §Ownership Model for the full rules.
