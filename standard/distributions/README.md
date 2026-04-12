# Archeia Distributions

A **distribution** is an opinionated bundle that extends [the Archeia Kernel](../KERNEL.md) for a specific audience. The kernel defines the abstract substrate — primitives, invariants, the three lifecycle shapes, the five kernel operations. A distribution makes the specific choices the kernel deliberately refuses to make.

This folder is where distributions live. Each distribution is one Markdown file declaring:

1. Its target audience
2. Its domain layout (usually but not always the five canonical software domains from [`SCHEMA.md`](../SCHEMA.md))
3. Its owner assignments per domain
4. Its status vocabularies and temporal mappings for transient artifacts
5. Its retention windows
6. Its inherent skill roster
7. Its agent roster (optional, but recommended)
8. Its ethos and philosophical commitments
9. Its workflow — how the domains connect in practice

The reference distribution is [`solo-builder.md`](solo-builder.md), which targets solo builders running AI-agent-maximalist bootstrapped software businesses. It's the distribution Archeia was designed for first; the kernel was extracted after the fact. Future distributions are expected — research labs, game studios, enterprise software teams, open-source projects with monetization intent, consulting practices. Each one extends the same kernel with its own opinions.

## Why distributions exist

The Archeia Kernel is small by design. It says things like:

- "A project has domains." (It doesn't say which ones, except that software-conforming projects use the five in [`SCHEMA.md`](../SCHEMA.md).)
- "Transient artifacts have retention windows." (It doesn't say how long.)
- "Domains have owners." (It doesn't say which agents or skills play which roles.)
- "Writers conform to schemas." (It doesn't say which skills to use.)

The kernel is audience-neutral. It would be the same for a kid tracking their weekend project, a team shipping enterprise SaaS, a research lab running experiments, or a law firm managing case files.

But a real user working on a real project needs all those choices made. Waking up and deciding "should my completed tasks live for 14 days or 90 days?" every morning is not a valuable exercise. Distributions make those choices ahead of time, on behalf of a specific audience, so that audience can skip the configuration and start using Archeia immediately.

A distribution is what happens when you take the kernel seriously and then get opinionated about who you're building for.

## The four things every distribution must provide

### 1. A `standard/domains.yaml` declaration

Lists the domains, their owners, their permitted shapes, and their cross-domain read relationships. Example:

```yaml
distribution: archeia-solo
version: 1.0.0

domains:
  - id: business
    owner: business-skills
    shapes: [living, accumulating, transient]
    reads: []
  - id: product
    owner: product-skills
    shapes: [living, accumulating]
    reads: [business, codebase]
  # ... other domains
```

For software distributions, the domain list should be the five canonical domains from [`SCHEMA.md`](../SCHEMA.md). For non-software distributions, declare whatever domains make sense for the audience (but be ready to defend why the five canonical ones don't fit).

### 2. A lifecycle specification for transient artifacts

For every transient artifact type, declare:

- Status vocabulary (e.g., `todo, active, done, cancelled`)
- Status → temporal mapping (`todo → future`, `active → present`, `done → past`)
- Retention window in days
- Terminal timestamp field name

Either embedded in `standard/domains.yaml` or in a separate `standard/lifecycles.yaml` — the kernel doesn't care which.

### 3. JSON Schemas under `standard/contracts/`

Enforceable schemas for every artifact type the distribution uses. At minimum:

- The kernel's three base schemas (`living-doc.schema.json`, `accumulating-record.schema.json`, `transient-artifact.schema.json`) — these can be inherited or re-exported
- The distribution's cross-domain contract schemas (for software distributions: `draft.schema.json`, `product.schema.json`, `c4.schema.json`)
- Any per-artifact-type schemas the distribution wants to enforce (e.g., `task.schema.json`, `adr.schema.json`)

### 4. The inherent skills plus whatever else the distribution ships

Every distribution MUST ship working implementations of the five inherent kernel skills (`archeia:init`, `archeia:validate`, `archeia:advance`, `archeia:complete`, `archeia:prune`) and the one inherent kernel agent (`archivist`). See [`KERNEL.md`](../KERNEL.md#6-inherent-skills) for the operation contracts.

A distribution MAY (and typically will) ship additional skills and agents that encode its opinionated workflow. Archeia Solo ships 16 skills and a growing agent roster.

## How to write a new distribution

1. **Pick an audience.** Be specific. "Solo builders shipping bootstrapped software" is specific. "Developers who want documentation" is not specific enough.
2. **Pick domains.** For software audiences, start with the five canonical domains in [`SCHEMA.md`](../SCHEMA.md) and only deviate if there's a real reason. For non-software audiences, design domains from scratch — but still keep the count small (three to seven is a good range).
3. **Pick shapes per artifact type.** Walk every artifact your audience needs and assign it a lifecycle shape. If you find yourself wanting a fourth shape, you've probably made a category error — look again.
4. **Pick retention windows.** For every transient artifact, how long does a terminal-state artifact live on disk before pruning? Default to short unless you have an audit requirement.
5. **Write the ethos.** What philosophical commitments does this distribution make? What scope decisions does it refuse to entertain? (Archeia Solo refuses VC-scale thinking, for example.)
6. **Ship the skills.** Implement the five inherent ones plus whatever workflow-specific skills your audience needs.
7. **Document all of the above in a single Markdown file in this folder.** Name the file after your distribution (e.g., `research-lab.md`, `game-studio.md`). Use `solo-builder.md` as a template.

## Distribution stability and compatibility

Distributions declare their own versioning, independently of the kernel version. A distribution may pin to a specific kernel version in its `standard/domains.yaml`:

```yaml
distribution: archeia-solo
version: 1.0.0
kernel: ">=0.1.0, <1.0.0"
```

When the kernel releases a new minor version, a distribution may choose to adopt new optional features or stay on the older minor. When the kernel releases a new major version, distributions are expected to update their pins and possibly their implementation.

Tools that consume `.archeia/` trees read the distribution name and version from `standard/domains.yaml` and adapt accordingly. A well-behaved tool that supports Archeia Solo 1.0 will degrade gracefully when asked to process an Archeia Research 0.3 tree — it will refuse with a clear error rather than corrupting the tree.

## Current roster

| Distribution | Audience | Status |
|---|---|---|
| [Archeia Solo](solo-builder.md) | Solo builders, one-person companies, AI-maximalist bootstrapped software shippers | **Reference distribution.** Ships 16 skills, a growing agent roster, and an opinionated ethos. This is the distribution the kernel was extracted from. |

Future distributions that I'd expect to exist within the next year:

- **Archeia Research** — research labs, experiment pipelines, publication workflows. Domains likely include `hypotheses/`, `experiments/`, `findings/`, `publications/`. Retention windows measured in months, not days.
- **Archeia Studio** — game studios, creative teams. Domains likely include `narrative/`, `assets/`, `playtest/`, `balance/`. Binary artifact support is load-bearing (sidecar-based provenance per the kernel's binary rules).
- **Archeia Enterprise** — compliance-heavy software environments. All transient retention windows are effectively 7 years (matching audit requirements), which means most "transient" artifacts are actually modeled as accumulating. Adds a formal review workflow on top of status transitions.
- **Archeia OSS** — open-source projects with monetization intent. Similar to Solo but adds a public-facing contributor workflow and a governance domain.

Distributions are not exclusive — a single organization can use multiple distributions across its projects. An indie developer might use Archeia Solo for their main product and Archeia Research for a side experiment. The kernel is the same; only the distribution choices differ.

## See also

- **[`../KERNEL.md`](../KERNEL.md)** — the abstract substrate distributions extend
- **[`../SCHEMA.md`](../SCHEMA.md)** — the canonical software application of the kernel (five domains, three contracts)
- **[`../PRINCIPLES.md`](../PRINCIPLES.md)** — the six fundamental truths that predate any specific distribution
- **[`../TEMPORAL_MODEL.md`](../TEMPORAL_MODEL.md)** — the three lifecycle shapes and their operations
