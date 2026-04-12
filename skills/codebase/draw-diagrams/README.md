# archeia:draw-diagrams

A skill that renders Mermaid architecture diagrams from `.archeia/` C4 JSON files so every system has visual topology alongside its structured data.

## What it does

Reads C4 JSON files produced by `archeia:write-tech-docs` and generates Mermaid diagrams in `.archeia/codebase/diagrams/`. Diagrams are views over structured data — they render what the JSONs describe, never invent entities.

| Diagram | Source | Mermaid Type | Limit | Condition |
|---------|--------|-------------|-------|-----------|
| System Context | System.json | flowchart TB | 12 nodes | Always |
| Container | Containers.json | flowchart TB | 15 nodes | When Containers.json exists |
| Primary Sequence | DataFlow.json | sequenceDiagram | 10 messages | When DataFlow.json exists |
| Entity-Relationship | Entities.json | erDiagram | 12 entities | When Entities.json exists |
| State Lifecycle | StateMachine.json | stateDiagram-v2 | 10 states | When StateMachine.json exists |
| Component Detail | Components.json | flowchart TB | 12 per container | When Components.json exists and 3+ containers have components |

## What it doesn't do

- Analyze the codebase (that's archeia:write-tech-docs)
- Generate directory-scoped README diagrams (that's archeia:write-readmes)
- Produce HTML, SVG, or PNG output (deployment concern, not protocol concern)
- Edit diagrams — it regenerates from scratch every time

## Prerequisites

Run `archeia:write-tech-docs` first. `System.json` is required. `Containers.json`, `Components.json`, and `DataFlow.json` may be absent by design when `archeia:write-tech-docs` emitted an insufficiency outcome, and this skill treats that as normal.

## Philosophy

See `references/DIAGRAM_PROTOCOL.md` for the full protocol — why diagrams are views not sources, why Mermaid, node limits as abstraction discipline, and how diagrams relate to the rest of the archeia pipeline.
