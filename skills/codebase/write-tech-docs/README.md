# archeia:write-tech-docs

Explores a repository and generates architecture documentation that both humans
and AI coding agents can use. Reads ~30 files (manifests, configs, CI, tests,
source samples, schema files), then produces a full documentation set grounded
in evidence — every claim cites a file path.

## What it produces

Up to nine `.archeia/` docs from structured templates in `assets/templates/`:

**Always generated:**

| Output | What it covers |
|--------|---------------|
| `Architecture.md` | System overview, topology, module boundaries, data flow, data model, state lifecycles |
| `System.json` | C4 Level 1 — system context diagram data |
| `Standards.md` | Language, formatting, linting, testing, naming conventions |
| `Guide.md` | Setup, dev commands, testing, common tasks |

**Always attempted:**

| Output | What it covers | Outcome rule |
|--------|---------------|--------------|
| `Containers.json` | C4 Level 2 — runtime units (API, DB, cache, workers) | Generate when one or more runtime units can be identified with evidence; otherwise emit an explicit insufficiency outcome instead of fabricating the file |
| `Components.json` | C4 Level 3 — code-level modules within each generated container | Generate when at least one generated container has evidence-backed internal source modules; otherwise emit an explicit insufficiency outcome instead of fabricating the file |
| `DataFlow.json` | Structured interaction records for sequence diagrams | Generate when a primary request/interaction flow can be traced with evidence; otherwise emit an explicit insufficiency outcome instead of fabricating the file |

**Conditional (when evidence supports):**

| Output | What it covers | Condition |
|--------|---------------|-----------|
| `Entities.json` | Domain entities, fields, relationships, cardinality | ORM/schema detected |
| `StateMachine.json` | State lifecycles with transitions and triggers | State machine library or clear lifecycle enums detected |

Plus two agent instruction files:
- `AGENTS.md` — synthesized project guidance for AI coding agents
- `CLAUDE.md` — pointer to AGENTS.md (avoids duplication)

`archeia:write-tech-docs` uses three output dispositions across its templates:
`always generated`, `always attempted`, and `conditional`. Attempted outputs
must be skipped with an explicit insufficiency outcome when the required
structure cannot be evidenced.

## How it works

1. **Explore** — runs `scripts/discover.sh` to get a default read plan, then
   reads manifests, configs, CI, tests, schema files, and source entry points.
   Signal priority: manifest content > file extensions > directory structure >
   README claims.
2. **Generate** — fills each template respecting `depends_on` ordering.
   Architecture.md first (no dependencies), then the always-attempted C4 and
   flow docs (`Containers.json`, `Components.json`, `DataFlow.json`), then
   conditional docs (Entities, StateMachine), then Standards and Guide. If
   any attempted JSON cannot be evidenced, the skill emits an explicit
   insufficiency outcome instead of fabricating it.
3. **Validate** — re-reads each output against its template's quality rubric,
   then runs `scripts/validate-evidence.sh` to verify canonical evidence paths
   in `.archeia/` docs and, after root docs are generated, in `AGENTS.md` and
   `CLAUDE.md`.
4. **Agent instructions** — synthesizes findings into AGENTS.md and CLAUDE.md.

## Script entrypoints

The skill now includes small helper scripts for deterministic exploration and
canonical evidence validation:

- `./scripts/discover.sh <repo-root>` — emits a JSON discovery plan with
  `files_to_read`, priority buckets, source roots, and repo signals.
- `./scripts/validate-evidence.sh <repo-root> [output-dir] [--include-root-docs]`
  — validates canonical evidence in Markdown `**Evidence:**` lines and JSON
  `evidence` arrays.

Typical usage:

```bash
./scripts/discover.sh /path/to/repo
./scripts/validate-evidence.sh /path/to/repo
./scripts/validate-evidence.sh /path/to/repo /path/to/repo/.archeia --include-root-docs
```

Validation exit codes:

- `0` — validation succeeded with no findings
- `2` — validation succeeded and reported invalid or malformed evidence
- `1` — bad arguments or runtime failure

## Skill structure

```
archeia:write-tech-docs/
├── SKILL.md                    — Workflow, phases, generation rules
├── README.md                   — This file
├── references/
│   ├── ARCHITECTURE_DOCS_PROTOCOL.md  — Philosophy: why .archeia/, evidence
│   │                                    principle, separation of concerns
│   └── examples.md             — Gold-standard output examples
├── assets/
│   └── templates/              — Structural exemplars for each output
│       ├── Architecture.md     — System-level map template
│       ├── System.json         — C4 Level 1 example
│       ├── Containers.json     — C4 Level 2 example
│       ├── Components.json     — C4 Level 3 example
│       ├── DataFlow.json       — Interaction records example
│       ├── Entities.json       — Entity-relationship model example
│       ├── StateMachine.json   — State lifecycle example
│       ├── Standards.md        — Conventions template
│       └── Guide.md            — Operational handbook template
├── scripts/
│   ├── discover.sh             — Deterministic exploration plan generator
│   ├── validate-evidence.sh    — Stable validator entrypoint
│   ├── validate_evidence.py    — Primary validator
│   └── validate_evidence_fallback.sh — Bash fallback validator
└── evals/
    └── evals.json              — Test cases for skill validation
```

## Prerequisites

Run `archeia:scan-repo` first for a quantitative snapshot. This skill
interprets and narrates; scan-repo counts and measures.
