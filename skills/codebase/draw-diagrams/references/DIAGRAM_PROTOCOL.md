# The Diagram Protocol

A protocol for generating and maintaining system-wide architecture diagrams as code.

---

## The Legibility Problem

The archeia pipeline produces accurate architecture documentation. Architecture.md
describes topology and data flow in prose. The C4 JSON templates (System.json,
Containers.json, Components.json) model the system as structured data with
evidence-grounded entities and relationships. Standards.md codifies conventions.
Guide.md covers operations.

The information is all there. But it fails at the one thing humans do best:
spatial reasoning.

A numbered data flow in Architecture.md tells you step 4 follows step 3. It
does not show you that the API server talks to three databases and the worker
only talks to one. A JSON file with 12 relationships is accurate. It is also
unreadable without tooling. Humans need topology visible at a glance — boxes,
arrows, boundaries. That is what diagrams provide.

But most architecture diagrams are created in Lucidchart or draw.io, exported
as PNGs, and placed in a `docs/` folder. Within weeks they are wrong. Nobody
updates them because the source of truth is a binary file in a tool most people
don't have open. The diagram becomes decoration — something you show in
onboarding and never look at again.

The fix is not better diagrams. It is a different relationship between diagrams
and data.

**Diagrams are a view, not a source.** They render what the JSON templates and
Architecture.md already describe. When the data changes, diagrams regenerate.
When a diagram looks wrong, you fix the data, not the diagram.

---

## Why Mermaid

Mermaid is text that renders as diagrams. It is the right default for
architecture visualization in code repositories because:

- **Diffable.** A changed relationship shows up in a pull request as a changed
  line. Reviewers see architecture changes alongside code changes.
- **No build step.** GitHub and GitLab render Mermaid natively in Markdown.
  VS Code previews inline. No image generation pipeline needed.
- **Agent-writable.** An AI agent can generate and update Mermaid without
  image-editing tools, screenshot comparisons, or binary file manipulation.
- **Colocated.** The diagram lives in the same repository as the code and
  the data it renders. No external tool, no separate account, no export step.

Mermaid covers the common cases well: flowcharts, sequence diagrams, entity-
relationship diagrams, state diagrams. For system-wide architecture views,
this is sufficient.

**Where Mermaid falls short:**

- The `C4Context` / `C4Container` diagram types exist but are experimental,
  inconsistently rendered across platforms, and limited in layout. Use standard
  `flowchart` with C4-style conventions (boundary subgraphs, labeled edges,
  technology annotations) instead.
- Layout control is limited. You cannot pin nodes to positions. Past ~15 nodes,
  readability degrades. This is a feature disguised as a limitation — it forces
  discipline in abstraction level.
- Complex ERDs with many cross-cutting relationships become spaghetti. Scope to
  key entities and primary relationships only.
- No native cloud or infrastructure icons. A VPC/ALB/S3 diagram in Mermaid
  looks like a generic flowchart — it adds nothing over the container diagram.

**The position:** Mermaid is the primary diagram language. It handles 80% of
architecture visualization needs. For the remaining 20% — detailed
infrastructure topology, large-scale dependency graphs, presentation-quality
C4 diagrams — teams can use D2 or Structurizr as escape hatches. The protocol
does not require them.

---

## The Diagram Suite

This protocol defines six diagram types. One is always generated, two are
source-available, and three are conditional. Mapping rules, examples, and
quality rubrics for each type are in the corresponding template in
`assets/templates/`.

| Diagram | Source | Template | Condition |
|---------|--------|----------|-----------|
| System Context | System.json | `context.md` | Always |
| Container | Containers.json | `containers.md` | When Containers.json exists |
| Primary Sequence | DataFlow.json | `sequence-primary.md` | When DataFlow.json exists |
| Entity-Relationship | Entities.json | `erd.md` | When Entities.json exists |
| State Lifecycle | StateMachine.json | `state-lifecycle.md` | When StateMachine.json exists |
| Component Detail | Components.json | `components.md` | When Components.json exists and 3+ containers have components |

`archeia:write-tech-docs` may intentionally omit `Containers.json`,
`Components.json`, or `DataFlow.json` when the corresponding structure cannot
be evidenced. Their absence is a valid protocol outcome, not an error.

---

## What Stays Out

| Content | Where it belongs | Why not here |
|---------|-----------------|--------------|
| Directory-scoped mermaid (max 10 nodes) | README.md via archeia:write-readmes | Local navigation aids, not system views |
| C4 structured data (JSON) | `.archeia/codebase/architecture/system.json`, `Containers.json`, `Components.json` | Data is the source; diagrams are the view |
| Text architecture descriptions | `.archeia/codebase/architecture/architecture.md` | Prose describes; diagrams visualize |
| Gantt charts, timelines, pie charts | Project management tools | Not architecture artifacts |
| UML class diagrams | Nowhere (or README if critical) | Code-level detail too volatile for maintained diagrams |
| Cloud infrastructure topology | D2, Structurizr, or IaC visualization tools | Mermaid lacks cloud icons; generic flowcharts duplicate the container diagram |
| Dependency graphs (npm, pip) | `npm ls`, `pipdeptree`, or similar CLI tools | Package-level detail, not architecture |

---

## Relationship to Existing Artifacts

Diagrams do not exist in isolation. They are a rendering layer over the
structured data that the archeia pipeline already produces.

| Source Artifact | Diagram |
|----------------|---------|
| `.archeia/codebase/architecture/system.json` | System Context |
| `.archeia/codebase/architecture/containers.json` (if present) | Container |
| `.archeia/codebase/architecture/components.json` (if present) | Component Detail |
| `.archeia/codebase/architecture/dataflow.json` (if present, primary flow) | Primary Sequence |
| `.archeia/codebase/architecture/entities.json` | Entity-Relationship |
| `.archeia/codebase/architecture/statemachine.json` | State Lifecycle |

**One source of truth, multiple views.** The JSON templates are the canonical
system model. Architecture.md is the canonical flow description. Diagrams
visualize them. README mermaid diagrams are separate — small, directory-scoped,
10-node-max navigation aids produced by archeia:write-readmes.

If a diagram contradicts its source, the source wins. Fix the source data and
regenerate the diagram. Never fix a diagram directly — the next regeneration
will overwrite the fix.

---

## Where Diagrams Live

System-wide diagrams live in `.archeia/codebase/diagrams/`, siblings of the JSON files
they render.

Naming convention:
- `context.md` — System Context
- `containers.md` — Container
- `sequence-primary.md` — Primary Sequence (additional sequences: `sequence-auth.md`, `sequence-payment.md`)
- `erd.md` — Entity-Relationship
- `state-[entity].md` — State Lifecycle (one per stateful entity)
- `components-[container].md` — Component Detail (one per container)

Files are Markdown wrapping Mermaid code blocks, not raw `.mmd` files. This
ensures GitHub renders them natively, and each file can carry a title heading
and an evidence citation block listing its source artifacts.

Directory-scoped diagrams remain in their respective `README.md` files. This
skill does not touch them.

---

## The Dual Output Question

The case for rendering diagrams in both Markdown and HTML is intuitive:
engineers see them in Git, stakeholders see them on a portal. In practice,
this creates a build step, output artifacts to manage, and a drift problem
when HTML gets out of sync with Markdown.

**This protocol produces Mermaid in Markdown. That is the output.**

GitHub and GitLab render Mermaid natively. Engineers see diagrams without
tooling. For teams that need HTML output — an internal developer portal, a
wiki, a presentation — the path is straightforward:

- `mermaid-cli` (`mmdc`) converts `.md` files to SVG or PNG
- `mermaid.ink` provides a URL-based rendering API
- Static site generators (Docusaurus, MkDocs) render Mermaid blocks in HTML

These are deployment concerns, not protocol concerns. The protocol defines
what diagrams exist, what data they render, and where they live. How a team
chooses to publish them beyond the Git repository is their decision.

---

## Diagrams as Thinking Tools

Mermaid text is editable in real time. Paste it into `mermaid.live`, change
a line, and the diagram updates instantly. This makes diagrams collaborative
tools, not just documentation artifacts.

In a meeting where someone says "actually, the API gateway talks directly to
the cache now," you edit three words in the Mermaid text and the diagram
reflects the new reality on screen. No switching to Lucidchart, no finding
the source file, no exporting a new PNG.

**Structure for editability.** One node definition per line. One relationship
per line. Consistent indentation. Comments for sections. A human or agent
should be able to add a node without understanding the entire diagram.

**But live edits are drafts, not truth.** Diagrams are a view over structured
data. If you sketch a new container in a meeting, that sketch must be
reconciled to Containers.json before it persists. The diagram is the
whiteboard; the JSON is the record. Sketching on the whiteboard is encouraged
for discussion — but the record is what the next regeneration reads.

---

## Maintenance in the Agentic Era

Diagrams are the only archeia artifact that is fully disposable.

READMEs accumulate learnings — tried approaches, dead ends, hard-won context
that cannot be regenerated from code analysis. Diagrams accumulate nothing.
Every element traces to a source artifact. Regeneration from scratch produces
an identical result (modulo layout).

This means:

- **Agents regenerate diagrams when source data changes.** When
  archeia:write-tech-docs updates the C4 JSONs, archeia:draw-diagrams
  regenerates the corresponding diagrams. No merge, no diff — full
  regeneration.
- **Manual diagram edits are not persisted.** If a human edits a diagram
  file directly, those edits are overwritten on the next regeneration. The
  fix is always: update the source artifact, then regenerate.
- **Diagrams never drift from reality.** Because they are derived, not
  authored, they are always as current as their source data. Stale source
  data produces stale diagrams — but the staleness is in the data, not the
  visualization.

This is a feature. It means a repository can have 10 diagrams without 10
maintenance burdens. The maintenance burden is on the source data, which
already exists and is already maintained.

---

## Design Decisions

### Flowchart over Mermaid C4 type

Mermaid has `C4Context` and `C4Container` diagram types. They are experimental,
inconsistently supported across rendering platforms, and limited in layout
options. A standard `flowchart` with C4-style conventions — boundary subgraphs,
labeled relationships, technology annotations in italics — produces diagrams
that render everywhere and look better. This is what the README Protocol
already uses for directory-scoped diagrams; the Diagram Protocol extends the
same approach to system-wide views.

### Render from JSON, don't duplicate

The C4 JSON templates are the canonical system model. Diagrams read from them.
They do not re-analyze the codebase independently. This means diagrams are
always consistent with the structured data and never introduce entities that
the JSONs don't know about. If a diagram needs a new entity, add it to the
JSON first.

### Node limits over completeness

A diagram with 30 nodes is not a diagram — it is a wall of text with arrows.
Strict node limits force the right level of abstraction at each zoom level.
If you need more detail, create a sub-diagram at the next zoom level (Container
→ Component), do not expand the current one.

### Markdown files, not raw .mmd

Diagram files are `.md` wrapping Mermaid code blocks, not bare `.mmd` files.
This ensures GitHub renders them natively, allows headings and evidence
citations alongside the diagram, and keeps files readable without specialized
tooling. A `.mmd` file requires a Mermaid-aware editor; a `.md` file renders
anywhere Markdown renders.

### No HTML generation in the protocol

HTML rendering is a deployment concern, not an architecture concern. Teams
that need HTML output for portals or presentations can add `mermaid-cli` or
static site generators downstream. The protocol produces the source of truth
(Mermaid in Markdown). Baking HTML generation into the protocol would mean
maintaining a build pipeline, managing output artifacts, and handling drift
between formats — exactly the problems that text-based diagrams were supposed
to eliminate.

### Sequence diagrams from structured data, not invention

The primary sequence diagram renders DataFlow.json's primary flow. It does not
invent interactions by analyzing import statements or guessing at runtime
behavior. If the JSON defines 6 steps, the sequence has 6 messages. This keeps
the diagram grounded in structured, evidence-backed data rather than
speculative code tracing.
