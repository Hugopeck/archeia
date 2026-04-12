---
name: write-tech-docs
version: 0.0.1
description: |
  Explore a repository and generate architecture documentation. Reads
  directory structure, manifests, configs, and imports, then generates
  up to nine `.archeia/` docs — four always (Architecture.md, System.json,
  Standards.md, Guide.md), attempts Containers.json, Components.json, and
  DataFlow.json on every run, and adds up to two more docs when evidence
  supports them (Entities.json, StateMachine.json) — plus AGENTS.md and
  CLAUDE.md. Uses structured templates, evidence grounding, and
  self-validation.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Edit
  - Write
---

## Purpose

This skill explores a repository and generates 6–11 files:

- 4 always-generated `.archeia/` docs from structured templates
  (Architecture.md, System.json, Standards.md, Guide.md)
- `Containers.json` is always attempted after `System.json`. Generate it
  only when one or more runtime units can be identified with evidence;
  otherwise emit an explicit insufficiency outcome and skip the file.
- `Components.json` is always attempted after the `Containers.json`
  decision. Generate it only when at least one generated container has
  evidence-backed internal source modules; otherwise emit an explicit
  insufficiency outcome and skip the file.
- `DataFlow.json` is always attempted after `Architecture.md`. Generate it
  only when a primary interaction flow can be traced with evidence;
  otherwise emit an explicit insufficiency outcome and skip the file.
- Up to 2 conditional `.archeia/` docs when evidence supports them
  (Entities.json, StateMachine.json)
- `AGENTS.md` — synthesized agent instructions from what was discovered
- `CLAUDE.md` — points to `AGENTS.md` to avoid duplication

Every claim in the generated docs must cite a file path as evidence. The
templates in `assets/templates/` define the structure, required sections,
and quality rubrics for each `.archeia/` file.

Read `references/ARCHITECTURE_DOCS_PROTOCOL.md` before starting. It explains
the philosophy behind `.archeia/` docs: why they live in the repo, what goes
in vs stays out, the evidence principle, the template-as-exemplar pattern,
and how `.archeia/` relates to READMEs, agents.md, and diagrams.

Read `references/examples.md` for gold-standard examples of the quality bar
this skill must hit. Study them before generating — they show the difference
between generic framework descriptions and genuinely useful architecture
documentation grounded in evidence.

<!-- TEMPLATE META-STRUCTURE
Every template in assets/templates/ follows a shared metadata contract:
1. Structural metadata (`layer`, `depends_on`, `required_evidence`, `validation`)
2. Purpose — what this document is and who reads it
3. Required Sections — sections that MUST appear in output
4. Conditional Sections — sections that appear only if evidence supports them
5. Inference Signals — what repo evidence maps to what content
6. Quality Rubric — completeness, truthfulness, conciseness, determinism
7. Anti-Patterns — DO NOT examples of bad output

Structural metadata fields:
- layer: 3 (auto-generate from evidence)
- depends_on: comma-separated template names that must be generated first
- required_evidence: comma-separated file patterns to read before generating
- validation: comma-separated quality checks for the self-validation pass

Generation disposition metadata:
- always_generated: the output file must be written on every run; gaps are
  recorded inside the generated file
- always_attempted: the template must be read on every run; write the output
  only when the required structure can be evidenced, otherwise emit an explicit
  insufficiency outcome and skip the file
- conditional: attempt generation only when the triggering evidence class
  exists; otherwise skip with an explicit reason

For Markdown templates, structural metadata lives in YAML frontmatter. For JSON
example templates, the skill infers the same contract from the template shape
plus the surrounding workflow rules. This metadata contract is consumed by the
skill — it is NOT included in generated output.
-->

## Workflow

### Phase 1: Exploration

Run `scripts/discover.sh <repo-root>` first and use its `files_to_read` array
as the default exploration plan. If `.archeia/codebase/scan-report.md` exists, use it as
supporting context, not required input. You may read beyond the discovery
output when manifests, imports, schema files, README claims, or workspace
structure point to additional evidence.

Then use this priority order for follow-up reads and overrides. Within each
category, read files alphabetically. Stop exploring after reading ~30 files
total — shift to generation if the budget is reached. If a critical file is
discovered late, reading it is fine.

**Priority 1 — Root manifests** (read all that exist):
`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`,
`composer.json`, `pom.xml`, `build.gradle`, `Mix.exs`, `deno.json`

**Priority 2 — Root configs** (read all that exist):
`tsconfig.json`, `tsconfig*.json`, `ruff.toml`, `pyproject.toml [tool.*]`,
`.eslintrc*`, `.prettierrc*`, `biome.json`, `Makefile`, `Justfile`,
`Taskfile.yml`, `Dockerfile`, `docker-compose.yml`, `fly.toml`, `render.yaml`,
`railway.json`, `vercel.json`, `netlify.toml`

**Priority 2.5 — Schema and model files** (read all that exist):
`prisma/schema.prisma`, `**/models.py`, `**/models/*.py`, `schema.graphql`,
`**/*.entity.ts`, `**/schema.ts` (Drizzle), `**/*.sql` in `migrations/` (first 2)

**Priority 3 — Root docs** (read all that exist):
`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`

**Priority 4 — CI/CD** (read first 3 files alphabetically):
`.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`

**Priority 5 — Test setup** (read config files, not test bodies):
`tests/conftest.py`, `jest.config.*`, `vitest.config.*`, `test/test_helper.*`,
`.nycrc`, `pytest.ini`, `setup.cfg [tool:pytest]`, `phpunit.xml`

**Priority 6 — Source sampling** (read first 5 files alphabetically):
Files in `src/`, `lib/`, `app/`, or the primary source directory. Focus on
entry points and module index files (`index.*`, `main.*`, `app.*`, `mod.rs`).

### Inference Signal Table

Use this table to map discovered files to conclusions. When signals conflict,
follow the priority order: **manifest content > file extensions > directory
structure > README claims**.

| Signal | Conclusion |
|--------|-----------|
| `package.json` exists | Node.js/JavaScript project |
| `package.json` has `"type": "module"` | ESM modules |
| `package.json` → `dependencies` has `react` | React frontend |
| `package.json` → `dependencies` has `express`/`fastify`/`hono` | HTTP server framework |
| `package.json` → `dependencies` has `next` | Next.js full-stack |
| `package.json` → `devDependencies` has `typescript` | TypeScript project |
| `package.json` → `scripts` has `test` | Has test runner |
| `tsconfig.json` exists | TypeScript (confirms) |
| `pyproject.toml` exists | Python project |
| `pyproject.toml` → `[tool.ruff]` | Uses ruff linter |
| `pyproject.toml` → `[tool.black]` | Uses black formatter |
| `pyproject.toml` → `[tool.mypy]` | Uses mypy type checker |
| `pyproject.toml` → `[tool.pytest]` | Uses pytest |
| `requirements.txt` / `setup.py` | Python (legacy packaging) |
| `Cargo.toml` exists | Rust project |
| `go.mod` exists | Go project |
| `Gemfile` exists | Ruby project |
| `composer.json` exists | PHP project |
| `pom.xml` / `build.gradle` | Java/JVM project |
| `Mix.exs` exists | Elixir project |
| `deno.json` exists | Deno runtime |
| `Dockerfile` exists | Containerized deployment |
| `docker-compose.yml` exists | Multi-service local dev |
| `fly.toml` | Deploys to Fly.io |
| `vercel.json` / `netlify.toml` | Serverless/JAMstack deploy |
| `render.yaml` / `railway.json` | PaaS deployment |
| `.github/workflows/` | GitHub Actions CI/CD |
| `.gitlab-ci.yml` | GitLab CI |
| `Makefile` / `Justfile` / `Taskfile.yml` | Has task automation |
| `tests/` / `__tests__/` / `spec/` / `test/` | Has test directory |
| `.pre-commit-config.yaml` | Uses pre-commit hooks |
| `src/` directory | Standard source layout |
| `lib/` directory | Library-style source layout |
| `app/` directory | Application-style layout (Rails, Next.js, etc.) |
| `packages/` / `apps/` | Monorepo with workspaces |
| `.env.example` | Environment-variable configuration |
| `uv.lock` / `poetry.lock` | Python lockfile (uv or poetry) |
| `pnpm-lock.yaml` / `package-lock.json` / `yarn.lock` | JS lockfile |
| `prisma` in manifest dependencies | Node.js project uses Prisma ORM |
| `prisma/schema.prisma` exists | Prisma schema file (read for entities) |
| `django` in manifest dependencies | Python project uses Django ORM |
| `**/models.py` with `class X(models.Model)` | Django models (read for entities) |
| `sqlalchemy` in manifest dependencies | Python project uses SQLAlchemy |
| `typeorm` in manifest dependencies | TypeScript project uses TypeORM |
| `drizzle-orm` in manifest dependencies | TypeScript project uses Drizzle ORM |
| `xstate` in manifest dependencies | Has explicit state machine library |
| `django-fsm` in manifest dependencies | Has Django finite state machine |
| Enum field named `status`/`state`/`phase` in model | Potential state lifecycle |

### Phase 2: Generation

Generate `.archeia/` docs in this order (respecting template `depends_on`):

1. Read `assets/templates/Architecture.md` frontmatter and body
2. Generate `.archeia/codebase/architecture/architecture.md` from collected signals
3. Read `assets/templates/System.json` example
4. Generate `.archeia/codebase/architecture/system.json` — follow the example structure exactly,
   replacing example data with evidence from this repo. Rules:
   - `system`: exactly one object, sourced from manifest + README
   - `people`: infer from README audience, auth roles, route groups. Empty `[]` if none found
   - `external_systems`: every external service confirmed by manifest deps or docker-compose
   - `relationships`: connect every entity. Every `source`/`target` must resolve to an `id` above
   - Every entity needs `evidence` array with at least one file path
   - IDs are kebab-case, deterministic from entity names
   - Descriptions are one sentence, no marketing language
   - Do NOT list internal modules as external systems
5. **Containers.json attempt** — Read `assets/templates/Containers.json`
   example on every run.
6. Attempt to generate `.archeia/codebase/architecture/containers.json`. If one or more runtime
   units can be identified with evidence, follow the example structure.
   Rules:
   - `system_boundary`: must match `system` from System.json (same id, name, description)
   - `containers`: runtime units (processes, databases, caches), NOT source directories.
     `type` is one of: `webapp | api | database | cache | queue | filesystem | worker | cli`
   - `external_systems`: carried forward from System.json, must match exactly
   - `relationships`: container-to-container and container-to-external
   - `people_container_mappings`: include only if System.json has people, omit key otherwise
   - For monoliths: still decompose if distinct runtime concerns exist
   - Infer from: docker-compose services, workspace packages, Dockerfiles, entry points
   If no evidence-backed runtime units can be identified:
   - Do NOT fabricate `.archeia/codebase/architecture/containers.json`
   - Mark the Architecture.md Topology section with
     `<!-- INSUFFICIENT EVIDENCE: runtime units for Containers.json -->`
   - Print: "Skipped Containers.json — no evidence-backed runtime units could be identified."
7. **Components.json attempt** — Read `assets/templates/Components.json`
   example on every run.
8. Attempt to generate `.archeia/codebase/architecture/components.json` after the
   `Containers.json` decision.
   - If `Containers.json` was generated and at least one container has
     evidence-backed internal source code, follow the example structure.
     Rules:
     - `containers`: one entry per container from Containers.json with internal source code.
       Skip containers with no app-side code (e.g., managed databases without schema code)
     - `components`: code-level modules (directories/packages, not files).
       `type` is one of: `module | service | controller | repository | middleware | handler | library | config`
       Prefix IDs with container ID (e.g., `api-routes`, `worker-jobs`)
     - `external_systems`: include only if components talk directly to externals
     - `relationships`: focus on architecturally significant connections (layer crossings,
       module boundaries, external integrations). Do NOT enumerate every import
     - Infer from: directory structure, import statements, module index files
     - Map Architecture.md Module Boundaries to components within containers
   - If `Containers.json` was skipped:
     - Do NOT fabricate `.archeia/codebase/architecture/components.json`
     - Mark the Architecture.md Module Boundaries section with
       `<!-- INSUFFICIENT EVIDENCE: Containers.json unavailable for Components.json -->`
     - Print: "Skipped Components.json — Containers.json was not generated."
   - If `Containers.json` was generated but no container has evidence-backed
     internal source modules:
     - Do NOT fabricate `.archeia/codebase/architecture/components.json`
     - Mark the Architecture.md Module Boundaries section with
       `<!-- INSUFFICIENT EVIDENCE: internal source modules for Components.json -->`
     - Print: "Skipped Components.json — no evidence-backed internal modules could be identified."
9. **Conditional: Entities.json** — Check if ORM/schema evidence was found
   during exploration (Prisma schema, Django models, SQLAlchemy models,
   TypeORM entities, Drizzle schema, or migration files with CREATE TABLE).
   If yes:
   - Read `assets/templates/Entities.json` example
   - Generate `.archeia/codebase/architecture/entities.json` — follow the example structure. Rules:
     - `source_type`: set based on detected ORM (prisma, django, sqlalchemy,
       typeorm, drizzle, sql, graphql)
     - `entities`: read schema/model files, extract domain entities only
       (not join tables, audit logs, migration tracking, or session tables)
     - `fields`: 3–6 key fields per entity. Include PKs, FKs, and
       domain-significant fields. Omit timestamps (created_at, updated_at)
       unless domain-relevant.
       `constraints` is one or more of:
       `pk | fk:[entity_id] | unique | not_null | nullable | default:[value]`
     - `relationships`: extract from FK fields and explicit relation decorators.
       `cardinality` is one of: `one_to_one | one_to_many | many_to_many`
     - Max 12 entities. If more exist, include the most interconnected ones.
     - Every entity and relationship needs `evidence` array
   If no ORM/schema evidence found, skip. Print: "Skipped Entities.json — no
   ORM or schema files detected."

10. **DataFlow.json attempt** — After Architecture.md Data Flow section is
    generated:
    - `assets/templates/DataFlow.json` is mandatory input. Read it on every
      run; this attempt is required even though the output file is
      evidence-gated.
    - Attempt to generate `.archeia/codebase/architecture/dataflow.json` on every run.
    - If a primary request or interaction flow can be traced with evidence:
      - Generate `.archeia/codebase/architecture/dataflow.json` — follow the example structure.
        Rules:
        - `flows`: at minimum one flow marked `primary: true`, matching
          Architecture.md's Data Flow table
        - `participants[].id` must resolve to an id in System.json,
          Containers.json, or Components.json.
          `type` is: `person | container | component | external_system`
        - `steps[].type` is: `sync | async | response`
        - `steps[].protocol` is: `HTTPS | SQL | gRPC | Redis | WebSocket |
          function call | message queue`
        - Include response steps for sync interactions (the return path)
        - Reading additional source files beyond the Phase 1 budget is
          allowed here — read route handlers and service files to trace the
          primary request path
        - Max 10 steps per flow. If the flow is longer, split into
          sub-flows or summarize middleware/validation as a single step.
    - If no evidence-backed flow can be traced:
      - Do NOT fabricate `.archeia/codebase/architecture/dataflow.json`
      - Mark the Architecture.md Data Flow section with
        `<!-- INSUFFICIENT EVIDENCE: primary interaction flow for DataFlow.json -->`
      - Print: "Skipped DataFlow.json — no evidence-backed request or
        interaction flow could be traced."

11. **Conditional: StateMachine.json** — Check if state machine evidence was
    found during exploration (explicit library in manifest, or clear enum
    fields with transition methods). If yes:
    - Read `assets/templates/StateMachine.json` example
    - Generate `.archeia/codebase/architecture/statemachine.json` — follow the example structure.
      Rules:
      - Only include state machines with `high` or `medium` confidence:
        - `high`: explicit library config (xstate createMachine, django-fsm
          decorator, aasm block)
        - `medium`: clear enum type + transition methods that reference the
          enum values
        - Do NOT include `low` confidence (inferred from if/else logic)
      - `state_machines[].entity` must resolve to an entity id in
        Entities.json (if generated). If no Entities.json, use descriptive id.
      - States: include all values from the enum/config. Max 10 per machine.
      - Transitions: trace from transition methods, guard functions, or state
        config. If a transition cannot be traced to source code, omit it
        rather than fabricate.
      - `terminal_states`: states with no outgoing transitions
    If no state machine evidence found, skip. Print: "Skipped
    StateMachine.json — no state machines or lifecycle enums detected."

12. Read `assets/templates/Standards.md` frontmatter and body
13. Generate `.archeia/codebase/standards/standards.md` (may reference Architecture.md for topology)
14. Read `assets/templates/Guide.md` frontmatter and body
15. Generate `.archeia/codebase/guide.md` (may reference Architecture.md + Standards.md)

For each generated file:
- Follow the template's Required Sections exactly
- Include Conditional Sections only when evidence supports them
- Cite evidence: every factual claim must reference a file path
- Use `<!-- INSUFFICIENT EVIDENCE: [description] -->` for gaps
- Do not include the template frontmatter in output
- Do not use marketing language or unsupported superlatives

### Phase 3: Self-Validation

After generating all `.archeia/` docs, run a validation pass:

**Step 1 — Rubric check:** Re-read each generated file. For each template's
quality rubric (listed at the bottom of the template), verify the output meets
every criterion. Fix issues inline using the Edit tool. One fix pass maximum —
if an issue persists after one fix attempt, note it and move on.

**Step 2 — Canonical evidence validation:** Run
`./scripts/validate-evidence.sh <repo-root>` after generating the `.archeia/`
docs. Fix any `invalid_paths` or `malformed_evidence` findings. The validator
checks only canonical evidence locations: Markdown `**Evidence:**` lines and
JSON `evidence` arrays.

**Step 3 — Validation summary:** Print a summary for the user:
- Number of docs generated
- Number of files read during exploration
- Number of issues found and fixed in validation
- Number of fabricated paths caught and removed
- Any remaining gaps or skipped outputs due to insufficient evidence

### Phase 4: Agent Instructions

After the `.archeia/` docs are validated, generate `AGENTS.md` and `CLAUDE.md`.

**AGENTS.md** — The substantive file. Synthesize what was discovered into
practical instructions that a coding agent needs when working in this repo.
Draw from the generated `.archeia/` docs:

- From Architecture.md: system overview, topology, module boundaries, data flow,
  data model, state lifecycles
- From Standards.md: language/runtime, formatting, linting, testing conventions
- From Guide.md: setup steps, dev commands, test commands, common tasks
- From the C4 diagrams that were generated: key containers, components, and
  their relationships
- From Entities.json (if generated): key domain entities and relationships
- From DataFlow.json (if generated): primary request flow participants and
  interactions
- From StateMachine.json (if generated): stateful entities and their lifecycles

Structure AGENTS.md following these best practices:
- Lead with a one-paragraph system overview
- List the tech stack (language, framework, package manager, key deps)
- Include setup and dev commands (copy from Guide.md findings)
- Document testing conventions and commands
- Note project structure and module boundaries
- Include coding standards (formatting, linting, naming)
- Keep it concise — agents reload this frequently, so brevity matters
- Every fact must trace back to evidence found during exploration
- End each factual section with a canonical `**Evidence:**` line using
  repo-relative inline-code paths so the final validation pass can verify it

**Handling low-confidence areas:** Architecture.md and Standards.md now
report confidence per section (high/medium/low). When generating AGENTS.md,
read the "Low-confidence guidance" blocks from both documents and translate
each one into a concrete agent instruction.

For each low-confidence area, AGENTS.md must explicitly state the absence
and provide a fallback behavior. Do not skip areas just because no
convention was detected — silence causes agents to hallucinate standards.

Example for a repo with mixed confidence:

```markdown
## Coding Standards

**Formatting:** No formatter configured. Match the style of the nearest
existing file. Do not introduce formatting tools without explicit approval.

**Linting:** ruff configured (`ruff.toml`). Run `ruff check` before
committing.

**Type checking:** No type checker configured. Do not add type annotations
unless the file already uses them.

**Testing:** pytest configured (`pyproject.toml`). Test files: `test_*.py`
in `tests/`. Run: `uv run pytest`.

**Naming:** Mostly snake_case. Some camelCase in `src/legacy/`. Match the
convention of the directory you're working in.
```

The pattern: for high-confidence areas, state the convention and the
command. For low-confidence areas, state the absence and the fallback
("match nearest file," "don't introduce," "ask first"). Every section
gets an entry — no gaps, no silence.

**CLAUDE.md** — A thin pointer file. Its only job is to direct Claude to
`AGENTS.md` so instructions are not duplicated across files. Format:

```markdown
# Claude Instructions

See [AGENTS.md](AGENTS.md) for full project instructions.
```

Add Claude-specific configuration below the pointer only if the repo has
Claude-specific needs (e.g., tool permissions, model preferences). Otherwise,
keep it minimal.

After generating `AGENTS.md` and `CLAUDE.md`, run
`./scripts/validate-evidence.sh <repo-root> <repo-root>/.archeia --include-root-docs`
so the final validation pass includes the generated root docs. This second pass
exists because root docs are produced in Phase 4, after the `.archeia/` docs.

## Operating Rules

- Every factual claim must cite a file path as evidence.
- When evidence is insufficient, use `<!-- INSUFFICIENT EVIDENCE: ... -->`.
- When `Containers.json`, `Components.json`, or `DataFlow.json` cannot be
  evidenced, skip the file and emit an explicit insufficiency outcome rather
  than inventing structure.
- When signals conflict, follow signal priority: manifest > extensions >
  structure > README claims.
- Prefer short, high-signal docs agents can reload frequently.
- Use template structure as the output skeleton, not as final prose.
- Do not invent technologies, frameworks, or dependencies not found in evidence.
- Do not use marketing language, superlatives, or filler phrases.

## Expected Outputs

`.archeia/` docs (always generated):
- `.archeia/codebase/architecture/architecture.md`
- `.archeia/codebase/architecture/system.json`
- `.archeia/codebase/standards/standards.md`
- `.archeia/codebase/guide.md`

`.archeia/` docs (always attempted):
- `.archeia/codebase/architecture/containers.json` (generate when one or more runtime units can be
  identified with evidence; otherwise emit an explicit insufficiency outcome)
- `.archeia/codebase/architecture/components.json` (generate when at least one generated container
  has evidence-backed internal source modules; otherwise emit an explicit
  insufficiency outcome)
- `.archeia/codebase/architecture/dataflow.json` (generate when a primary interaction flow can be
  traced with evidence; otherwise emit an explicit insufficiency outcome)

Conditional `.archeia/` docs (when evidence supports):
- `.archeia/codebase/architecture/entities.json` (when ORM/schema detected)
- `.archeia/codebase/architecture/statemachine.json` (when state machines detected)

Agent instructions:
- `AGENTS.md`
- `CLAUDE.md`
