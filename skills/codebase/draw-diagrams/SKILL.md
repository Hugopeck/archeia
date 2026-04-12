---
name: draw-diagrams
version: 0.0.1
description: |
  Render Mermaid diagrams from .archeia/ JSON files. Reads System.json and,
  when present, Containers.json, Components.json, DataFlow.json,
  Entities.json, and StateMachine.json. Produces .archeia/codebase/diagrams/ with
  context, container, sequence, erd, state, and component diagrams.
  Diagrams are views over structured data — fully regenerable, never
  manually edited. Requires archeia:write-tech-docs to have been run first.
  Use this skill when the user wants to generate architecture diagrams,
  visualize their system, or create Mermaid diagrams from existing .archeia/
  documentation.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Write
---

## Purpose

This skill renders Mermaid diagrams from the C4 JSON files that
`archeia:write-tech-docs` produces. It does not analyze the codebase. It does
not invent entities. It reads structured data and writes diagrams — a pure
transformation from JSON to Mermaid.

Read `references/DIAGRAM_PROTOCOL.md` before starting. It explains why diagrams
are views not sources, why Mermaid over other formats, how node limits enforce
abstraction discipline, and the file structure conventions.

The core principle: **if it's not in the JSON, it's not in the diagram.** Every
node traces to an entity. Every edge traces to a relationship. When a diagram
looks wrong, the fix is in the source JSON — not in the diagram.

Diagrams are fully disposable. This skill regenerates every diagram from scratch
each time it runs. It never patches or diffs existing diagram files.

<!-- TEMPLATE META-STRUCTURE
Every template in assets/templates/ follows this structure:
1. YAML frontmatter (source, mermaid_type, limit, depends_on, condition, validation)
2. Purpose — what question this diagram answers
3. Mapping Rules — JSON field → Mermaid syntax, numbered
4. Node ID Convention — how to convert entity IDs for this diagram type
5. Shape/Arrow/Cardinality Convention — which Mermaid shapes or arrows to use
6. Example Transformation — complete input JSON + output Markdown
7. Quality Rubric — traceability, completeness, labeling, limits
8. Anti-Patterns — DO NOT examples specific to this diagram type

Frontmatter fields:
- source: the .archeia/ JSON file this diagram reads
- mermaid_type: the Mermaid diagram type keyword
- [type]_limit: hard limit on nodes/messages/entities/states/components
- depends_on: source artifact that must exist
- condition: always | source-available criteria | conditional criteria
- validation: comma-separated quality checks for the validation pass

The skill reads frontmatter to determine generation conditions and validation
criteria. Frontmatter is consumed by the skill — it is NOT included in
generated output.
-->

## Workflow

### Phase 1: Read Source Data

**Step 1 — Verify prerequisites.**

Check that `.archeia/` exists in the target repo. If it doesn't, stop:
"Run archeia:write-tech-docs first — this skill renders diagrams from .archeia/
JSON files."

**Step 2 — Read source JSON files.**

Read the one required file:
- `.archeia/codebase/architecture/system.json`

If it is missing, stop: "Run archeia:write-tech-docs first — missing
System.json."

Check for source-available files:
- `.archeia/codebase/architecture/containers.json`
- `.archeia/codebase/architecture/components.json`
- `.archeia/codebase/architecture/dataflow.json`

Check for conditional files:
- `.archeia/codebase/architecture/entities.json` — if present, will generate ERD
- `.archeia/codebase/architecture/statemachine.json` — if present, will generate state diagrams

For each file that exists, parse it and verify the expected top-level keys:
- System.json: `system`, `people`, `external_systems`, `relationships`
- Containers.json: `system_boundary`, `containers`, `external_systems`, `relationships`
- Components.json: `containers`, `relationships`
- DataFlow.json: `flows`
- Entities.json: `source_type`, `entities`, `relationships`
- StateMachine.json: `state_machines`

Absence of `Containers.json`, `Components.json`, or `DataFlow.json` is normal
when `archeia:write-tech-docs` emitted an insufficiency outcome. Do not treat
that as a prerequisite failure.

**Step 3 — Determine generation plan.**

Always generate:
1. `context.md` from System.json

Generate when the source JSON exists:
2. `containers.md` from Containers.json
3. `sequence-primary.md` from DataFlow.json
4. `sequence-[flow-id].md` — only if DataFlow.json exists and has non-primary flows

Conditionally generate:
5. `erd.md` — only if Entities.json exists
6. `state-[entity].md` — only if StateMachine.json exists (one per state machine)
7. `components-[container].md` — only if Components.json exists and 3 or more
   containers have non-empty `components` arrays

**Step 5 — Create output directory.**

```bash
mkdir -p .archeia/codebase/diagrams
```

---

### Phase 2: Base and Source-Available Diagrams

For each diagram in this phase, read its template from `assets/templates/`,
apply the mapping rules to the source JSON, and write the output file to
`.archeia/codebase/diagrams/`. Each template contains the complete transformation
logic: mapping rules, ID conventions, shape conventions, an example
transformation, a quality rubric, and anti-patterns.

#### 2a. System Context (`context.md`)

Read `assets/templates/context.md` frontmatter and body. Apply its mapping
rules to `.archeia/codebase/architecture/system.json`. Write `.archeia/codebase/diagrams/context.md`.

The system goes inside a boundary subgraph. People get stadium shapes.
External data stores get cylinder shapes. All edges are labeled.
Node limit: 12.

#### 2b. Container Diagram (`containers.md`)

**Condition:** `.archeia/codebase/architecture/containers.json` exists. If it doesn't, skip. Print:
"Skipped containers.md — Containers.json not found."

Read `assets/templates/containers.md` frontmatter and body. Apply its mapping
rules to `.archeia/codebase/architecture/containers.json`. Write `.archeia/codebase/diagrams/containers.md`.

Containers go inside the system boundary subgraph. People and external systems
go outside. People-container mappings become additional edges.
Node limit: 15.

#### 2c. Primary Sequence (`sequence-primary.md`)

**Condition:** `.archeia/codebase/architecture/dataflow.json` exists. If it doesn't, skip. Print:
"Skipped sequence diagrams — DataFlow.json not found."

Read `assets/templates/sequence-primary.md` frontmatter and body. Apply its
mapping rules to `.archeia/codebase/architecture/dataflow.json` (the flow with `primary: true`).
Write `.archeia/codebase/diagrams/sequence-primary.md`.

Each step becomes a message with the correct arrow type: sync `->>`、async
`-)`, response `-->>`. Participant IDs use the raw `id` (no UPPER_SNAKE_CASE
— sequence diagrams handle hyphens). Message limit: 10.

If DataFlow.json contains non-primary flows, generate a separate file for
each: `sequence-[flow-id].md`. Apply the same template rules.

---

### Phase 3: Conditional Diagrams

#### 3a. Entity-Relationship (`erd.md`)

**Condition:** `.archeia/codebase/architecture/entities.json` exists.
If it doesn't, skip. Print: "Skipped erd.md — Entities.json not found."

Read `assets/templates/erd.md` frontmatter and body. Apply its mapping rules
to `.archeia/codebase/architecture/entities.json`. Write `.archeia/codebase/diagrams/erd.md`.

Entity names use UPPER_SNAKE_CASE. Cardinality maps to Mermaid symbols
(`one_to_many` → `||--o{`). Entity limit: 12.

#### 3b. State Lifecycle (`state-[entity].md`)

**Condition:** `.archeia/codebase/architecture/statemachine.json` exists.
If it doesn't, skip. Print: "Skipped state diagrams — StateMachine.json not found."

Read `assets/templates/state-lifecycle.md` frontmatter and body. Generate one
file per entry in `state_machines`. Name each file using the `entity` field:
`state-task.md`, `state-order.md`.

State names convert from snake_case to PascalCase. Initial states get `[*] -->`
entry markers. Terminal states get `--> [*]` exit markers. State limit: 10.

#### 3c. Component Detail (`components-[container].md`)

**Condition:** `.archeia/codebase/architecture/components.json` exists and has 3 or more containers
with non-empty `components` arrays. If the file does not exist, skip. Print:
"Skipped component diagrams — Components.json not found." If the file exists
but the condition is not met, skip. Print: "Skipped component diagrams —
fewer than 3 containers have internal components."

Read `assets/templates/components.md` frontmatter and body. Generate one file
per container that has components. Name each file using the container's `id`:
`components-api-server.md`, `components-background-worker.md`.

Only include external systems and relationships that touch this container's
components. Component limit: 12 per container.

---

### Phase 4: Validation and Report

After generating all diagrams, validate each file against its template's
quality rubric.

**Step 1 — Structure check.** Every diagram file must:
- Start with a `# ` heading
- Contain exactly one fenced mermaid code block
- End with `**Source:**` and `**Generated:**` citation lines

Fix any structural issues.

**Step 2 — Node traceability check.** For each diagram, verify:
- Every node ID in the Mermaid corresponds to an entity `id` in the source JSON
- Every edge corresponds to a relationship in the source JSON
- No nodes or edges were invented

If you find a node or edge that doesn't trace to the JSON, remove it.

**Step 3 — Limit check.** Verify node/message counts against template limits:
- context.md: 12 nodes max
- containers.md: 15 nodes max
- sequence-primary.md: 10 messages max
- erd.md: 12 entities max
- state-[entity].md: 10 states max
- components-[container].md: 12 components max

**Step 4 — Edge label check.** Verify every edge has a label. Unlabeled
edges are ambiguous. If an edge is missing a label, use the `description`
from the source relationship.

**Step 5 — Report.** Print a summary:

```
Diagram generation complete.

Generated: 5
  - .archeia/codebase/diagrams/context.md (7 nodes)
  - .archeia/codebase/diagrams/containers.md (8 nodes)
  - .archeia/codebase/diagrams/sequence-primary.md (6 messages)
  - .archeia/codebase/diagrams/erd.md (3 entities)
  - .archeia/codebase/diagrams/state-task.md (5 states)

Skipped: 1
  - components-*.md — fewer than 3 containers have internal components
```

## Output File Structure

Every generated diagram file follows this exact structure — heading, mermaid
block, citation. No prose paragraphs, no explanatory text, no extra sections.

````markdown
# [Diagram Title]

```mermaid
[diagram content — one node/edge per line, 4-space indentation]
```

**Source:** `.archeia/codebase/architecture/[SourceFile.json]`
**Generated:** YYYY-MM-DD
````

Use today's date for the Generated field.

## Quality Rules

These rules apply universally across all diagram types. Per-diagram quality
rubrics with type-specific checks are in each template's Quality Rubric section.

- **Every node traces to a JSON entity.** No invented boxes. If a node ID
  doesn't correspond to an `id` in the source JSON, delete it.
- **Every edge traces to a JSON relationship.** No invented arrows. If an edge
  doesn't correspond to a `relationships` entry, delete it.
- **Edge labels are mandatory.** Every arrow must have a label from the source
  `description` field. Unlabeled arrows are ambiguous.
- **Node limits are hard limits.** Never exceed them. When trimming, prioritize
  nodes that appear in the most relationships.
- **Technology annotations.** Use `Name<br/><i>Technology</i>` format in
  flowchart nodes where the entity has a `technology` field.
- **One definition per line.** Each node definition and each edge on its own
  line. This makes diffs readable and editing predictable.
- **Consistent indentation.** 4 spaces inside mermaid blocks.
- **Full regeneration.** Never read existing diagram files. Always write from
  scratch. Do not attempt to diff or merge.

## Anti-Patterns

These are universal anti-patterns. Per-diagram anti-patterns with type-specific
examples are in each template's Anti-Patterns section.

- **Inventing nodes.** Adding a "Load Balancer" because most systems have one,
  even though it's not in System.json. The JSON is the source of truth.
- **Exceeding node limits.** A 20-node container diagram is a wall of text,
  not a visualization. Trim to the limit.
- **Unlabeled edges.** An arrow from A to B with no label could mean anything.
  Always label.
- **Using Mermaid C4Context/C4Container types.** These are experimental and
  render inconsistently. Use `flowchart` with boundary subgraphs instead.
- **Generating diagrams for missing sources.** If Containers.json,
  Components.json, DataFlow.json, or Entities.json doesn't exist, don't
  generate the corresponding diagram. Missing source files can be an explicit,
  correct outcome from `archeia:write-tech-docs`.
- **Adding prose to diagram files.** Diagram files are heading + mermaid +
  citation. No paragraphs, no explanations, no tables.
- **Editing diagrams to fix errors.** If a diagram is wrong, the source JSON
  is wrong. Fix the JSON. The next regeneration fixes the diagram.
- **Merging with existing diagrams.** This skill overwrites. Old diagrams are
  disposable.

## Expected Output

`.archeia/codebase/diagrams/` containing:

Always generated:
- `context.md` — System Context (from System.json)

Generated when source JSON exists:
- `containers.md` — Container Diagram (from Containers.json)
- `sequence-primary.md` — Primary Sequence (from DataFlow.json)
- `sequence-[flow-id].md` — Additional sequences for non-primary flows (from DataFlow.json, when additional flows exist)

Conditionally generated:
- `erd.md` — Entity-Relationship (from Entities.json, when it exists)
- `state-[entity].md` — State Lifecycle, one per state machine (from StateMachine.json, when it exists)
- `components-[container].md` — Component Detail, one per container (from Components.json, when 3+ containers have components)
