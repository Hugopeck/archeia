# Archeia Solo — Distribution for Solo Builders

> **The reference distribution.** Archeia Solo is the complete, unapologetically opinionated extension of [the Archeia Kernel](../KERNEL.md) for one specific audience: solo operators running bootstrapped software businesses with AI agents doing the bulk of the work. It ships 16 skills, a growing agent roster, explicit retention windows, and a philosophical ethos that refuses several framings (VC logic, PMF rituals, team-later assumptions) on purpose.
>
> If you're a solo builder shipping AI-assisted software that needs to earn from day one, this is the distribution you install. If you're any other kind of builder, this is still the best-documented Archeia distribution to read as a reference before writing your own.

---

## 1. Audience

Archeia Solo is for **one specific kind of operator**: someone who directs AI agents to build and ship revenue-earning software products, with no team to hire, no runway to burn, no VC to please, and no illusion that scale justifies unprofitable work.

**Specifically:**

- **One operator.** Zero employees. Agents as force multipliers, not as teammates. Decisions are fast because one person makes them.
- **Bootstrapped.** Revenue from day one, or the project doesn't exist. No VC, no angel, no friends-and-family round.
- **AI-maximalist.** The operator routes work to agents aggressively. Writing code by hand is the exception, not the default. The skill is orchestration, not typing.
- **Shipping.** The product is real, it ships, it's used by real buyers who pay real money. Not a prototype, not a demo, not a side project to impress a conference audience.
- **Personal-pain-driven.** The operator is solving their own problem, or a problem they've felt intimately enough to be trusted on. Specificity beats generality.
- **Revenue over growth.** Sustainable small businesses over sprawling growth machines. Hyper-growth is not the goal; profitable steady shipping is.

**Who Archeia Solo is NOT for:**

- VC-backed startups with runway to burn
- Teams larger than 2-3 people (even with agents — the ethos assumes one decision-maker)
- Enterprise software with compliance reviews (retention windows are wrong; governance assumptions are wrong)
- Non-software projects (pick a different distribution or write one)
- Hobby projects with no monetization intent (the ethos hurts more than it helps)

These audiences have different needs and deserve their own distributions. Don't force Archeia Solo on a user it wasn't built for.

---

## 2. Kernel conformance

Archeia Solo conforms to the [Archeia Kernel](../KERNEL.md) version `0.1.0` and uses the five canonical software domains from [`SCHEMA.md`](../SCHEMA.md). It does not add or remove domains. It does not add new lifecycle shapes. It picks specific owners, specific status vocabularies, specific retention windows, and specific skills — but nothing above the kernel line is modified.

**`standard/domains.yaml` for Archeia Solo:**

```yaml
distribution: archeia-solo
version: 1.0.0
kernel: ">=0.1.0, <1.0.0"

domains:
  - id: business
    owner: product-skills
    shapes: [living, accumulating, transient]
    reads: []
  - id: product
    owner: product-skills
    shapes: [living, accumulating]
    reads: [business, codebase]
  - id: codebase
    owner: codebase-skills
    shapes: [living]
    reads: [product]
  - id: growth
    owner: growth-skills
    shapes: [living, accumulating, transient]
    reads: [business, product]
  - id: execution
    owner: execution-skills
    shapes: [accumulating, transient]
    reads: [product, codebase]

contracts:
  - from: business
    to: product
    schema: standard/contracts/draft.schema.json
  - from: product
    to: execution
    schema: standard/contracts/product.schema.json
  - from: codebase
    to: product
    schema: standard/contracts/c4.schema.json
```

Note that in Archeia Solo, `business/` is owned by `product-skills`. This is a known interim arrangement — the product-ideation skills (`clarify-idea`, `create-vision`) live under `skills/product/` and write to `.archeia/business/`. A future version may split this into a dedicated `business-skills` owner, but as of 1.0 the solo operator uses the same skill family for both domains.

---

## 3. Skill roster

Archeia Solo ships 16 skills organized by domain. All install under the `archeia:` namespace via `install.sh`.

### Product domain (4 skills)

| Skill | What it does | Shape it writes to |
|---|---|---|
| **`archeia:clarify-idea`** | Explore and sharpen a rough product idea. Save a design brief to `.archeia/business/drafts/`. Includes alternatives, optional UI mockup, and solo-builder ethos enforcement. | Transient (draft) |
| **`archeia:create-vision`** | Pressure-test a plan. Save a vision artifact to `.archeia/business/vision/vision.md` (updating the living doc in place). Modes: scope expansion / selective / hold / reduction. | Living (vision.md) |
| **`archeia:review-draft`** | Convert a reviewed draft into the locked product spec. Reads draft + optional codebase feasibility. Writes updates to `.archeia/product/product.md` (living doc) and records the decision in `.archeia/product/decisions/`. Marks the source draft as `advanced`. | Living (product.md) + Accumulating (decision) |
| **`archeia:lock-spec`** | Append an ADR-style decision record to `.archeia/product/decisions/`. Typically called internally by `review-draft` but also invocable for manual decision-capture. | Accumulating (decision) |

### Codebase domain (6 skills)

| Skill | What it does | Shape it writes to |
|---|---|---|
| **`archeia:scan-repo`** | Scan the repo for quantitative metrics: LOC, dependencies, test coverage, README gaps. Produces `.archeia/codebase/scan-report.md`. | Living (scan-report.md) |
| **`archeia:scan-git`** | Analyze git history: contributors, bus factor, churn, velocity. Produces `.archeia/codebase/git-report.md`. | Living (git-report.md) |
| **`archeia:write-tech-docs`** | Generate architecture documentation. Produces `.archeia/codebase/architecture/architecture.md`, the C4 JSONs, `.archeia/codebase/standards/standards.md`, `.archeia/codebase/guide.md`, and root `AGENTS.md`/`CLAUDE.md`. Evidence-gated: every claim cites a file path. | Living (multiple) |
| **`archeia:write-readmes`** | Generate colocated `README.md` files per directory, driven by scan-report coverage gaps. | Living (colocated) |
| **`archeia:write-agents-docs`** | Generate colocated `agents.md` + `claude.md` files per directory where local rules differ from root. | Living (colocated) |
| **`archeia:draw-diagrams`** | Render Mermaid diagrams from the C4 JSONs into `.archeia/codebase/diagrams/`. | Living (*.mmd) |

### Execution domain (6 skills, ported from track)

| Skill | What it does | Shape it writes to |
|---|---|---|
| **`archeia:work`** | Runs the active work session. Handles tracked and untracked modes, task lifecycle transitions, PR state tracking. | Transient (task frontmatter) |
| **`archeia:create`** | Create projects and tasks from natural language. Reads `.archeia/product/product.md` when present to ground task generation in the locked spec. | Transient (projects, tasks) |
| **`archeia:decompose`** | Break a project brief into parallel task files. Uses subagent delegation for parallel exploration of the codebase. | Transient (tasks) |
| **`archeia:setup-track`** | Scaffold `.archeia/execution/` in an adopting repo. Template readmes only — the full bash enforcement layer (hooks, workflows, ruleset) is preserved in the archived track repo for selective backport. | Scaffolds directories |
| **`archeia:todo`** | Regenerate `BOARD.md`, `TODO.md`, `PROJECTS.md` views. **Currently pending**: requires `track-todo.sh` which was not ported in Phase 2. | Derived views |
| **`archeia:update-track`** | Auto-update installed skills at session start. | Maintenance |

### Kernel-inherent skills

Per [`KERNEL.md`](../KERNEL.md#6-inherent-skills), every distribution must provide implementations of:

- **`archeia:init`** — scaffold `.archeia/` and its five domains for a new project
- **`archeia:validate`** — walk the tree and check conformance against schemas and shapes
- **`archeia:advance`** — promote a transient artifact from future-status to present-status
- **`archeia:complete`** — promote a transient artifact from present-status to past-status and start the retention clock
- **`archeia:prune`** — delete expired transient artifacts (retention window elapsed)

These are **pending implementation** in Archeia Solo 1.0. The current 16 skills cover the workflow but the five kernel-inherent operations are implicit in how `archeia:work`, `archeia:create`, and the others handle status transitions. Explicit implementations of the five inherent skills are planned for the next minor version.

---

## 4. Agent roster

Archeia Solo ships personal Claude Code subagents in [`agents/`](../../agents/). As of 1.0:

| Agent | Role | Reads | Writes |
|---|---|---|---|
| [`architect`](../../agents/architect.md) | System architecture, feasibility, ADR authoring | `.archeia/codebase/architecture/**`, `.archeia/product/product.md`, `.archeia/business/drafts/*.md`, `.archeia/product/decisions/*.md` | `.archeia/product/decisions/*.md` (when decision-grade) |
| [`engineer`](../../agents/engineer.md) | Implementation — task spec to working code | `.archeia/execution/tasks/<active>.md`, `.archeia/product/product.md`, `.archeia/codebase/standards/standards.md`, `.archeia/codebase/guide.md` | Source files, task frontmatter updates |

**Expected additions in future minor versions:**

- **`archivist`** — handles supersession, pruning, and history queries. Required by the kernel but not yet shipped in Solo 1.0.
- **`designer`** — UI/UX, interaction patterns, visual direction. Reads `.archeia/product/design/` and `.archeia/business/vision/vision.md`.
- **`pm`** — product management, scope decisions, stakeholder language. Reads `.archeia/business/` and `.archeia/product/`.
- **`qa`** — testing, edge cases, verification. Reads `.archeia/execution/tasks/` and `.archeia/codebase/guide.md` (for test commands).
- **`researcher`** — market research, competitor analysis, prior art. Reads `.archeia/business/landscape/`.

Agents install to `~/.claude/agents/` (user-level) via `install.sh`, making them available in every repo the operator opens — not just Archeia-conforming ones.

---

## 5. Status vocabularies and temporal mappings

Transient artifacts in Archeia Solo use these status vocabularies and temporal mappings.

### Tasks (`execution/tasks/*.md`)

| Status | Temporal | Meaning |
|---|---|---|
| `todo` | future | Created but not started. Sits in the backlog. |
| `backlog` | future | Deliberately deferred. Not the next thing to pick up. |
| `active` | present | Work is in progress. Exactly one task per operator should be `active` at a time. |
| `review` | present | Work is done; PR is open; waiting on CI, code review, or self-review. |
| `done` | past | Work is complete, PR merged. **Terminal timestamp: `completed`.** |
| `cancelled` | past | Work was abandoned before completion. **Terminal timestamp: `cancelled_at`.** |

**Retention window:** 14 days after terminal status.

### Plans (`execution/plans/*.md`)

| Status | Temporal | Meaning |
|---|---|---|
| `proposed` | future | Drafted but not yet adopted. |
| `current` | present | The operator is actively working against this plan. |
| `superseded` | past | Replaced by a newer plan. **Terminal timestamp: `superseded_at`.** |

**Retention window:** 30 days after terminal status.

### Projects (`execution/projects/*.md`)

| Status | Temporal | Meaning |
|---|---|---|
| `proposed` | future | Drafted but not yet decomposed or started. |
| `active` | present | Decomposed into tasks, work is in progress. |
| `completed` | past | All tasks done, project shipped. **Terminal timestamp: `completed`.** |
| `cancelled` | past | Abandoned. **Terminal timestamp: `cancelled_at`.** |

**Retention window:** 60 days after terminal status.

### Drafts (`business/drafts/*.md`)

| Status | Temporal | Meaning |
|---|---|---|
| `draft` | future | Being written. |
| `review` | future | Under consideration; a product writer may advance it. |
| `advanced` | past | Merged into a living document (vision.md or product.md). **Terminal timestamp: `advanced_at`.** |
| `discarded` | past | Rejected. **Terminal timestamp: `discarded_at`.** |

**Retention window:** 0 days for `discarded` (pruned immediately). 7 days for `advanced`.

### Running growth experiments (`growth/experiments/*.md`)

| Status | Temporal | Meaning |
|---|---|---|
| `proposed` | future | Hypothesis written, not yet running. |
| `running` | present | Experiment is live. |
| `concluded` | past | Experiment is over. If there are learnings worth keeping, the file is promoted to an accumulating record (written to `growth/experiments/` with a permanent `status: archived`). Otherwise, it enters the retention window. **Terminal timestamp: `concluded`.** |

**Retention window:** 7 days for `concluded` experiments without learnings. Experiments with learnings are promoted to accumulating records and never pruned.

---

## 6. The ethos

Archeia Solo makes philosophical commitments no other distribution will make. These are not optional — they're the whole point.

### Boil the Lake, not the Ocean

AI makes completeness near-free. Take the complete version of every boilable task. Don't ship 90% when the last 10% is cheap. Lakes (tasks that can be fully explored in a session) are boilable; oceans (tasks that require weeks and specialized knowledge) are not — flag the oceans, boil the lakes.

In practice: when running a skill, always generate alternatives instead of stopping at the first idea. Write the full brief instead of scattered notes. Include edge cases and open questions. Produce the mockup when the idea has a UI surface.

### Revenue is the Signal

Every feature must map to something a real buyer will pay for. Free tools, prototypes, and demos are rejected — not because they're bad, but because this distribution is for people who need to earn. If the path from this feature to a paying customer is unclear, name that as a gap and resolve it before building.

### User Sovereignty

The operator has context the agents don't. Agents recommend; the operator decides. Always present options using the AskUserQuestion format. Never silently commit to a path. Never pretend the agent knows best when the operator has signal the agent can't see.

### Search Before Building

Before writing new code or a new skill, check what already exists: in the current repo, in prior artifacts, in the installed skill library, in the operator's other projects. Reinventing something that already works is a tax paid for no reason.

### Personal Pain to Paying Customer

Solve your own problem, or a problem you've felt intimately enough to be trusted on. The specificity of lived experience beats the generality of hypothetical users. If you can't name a specific customer who has this pain and will pay to remove it, you don't have a product — you have a guess.

### Bootstrap Discipline

Every scope decision must be achievable by one operator plus AI, without outside capital or a team to hire. If shipping requires a team or investors, the scope is too big. Low-to-mid scale is a valid and complete outcome — a focused product with paying customers and healthy margins is a better outcome than a sprawling product chasing hypothetical growth.

### Ship Fast, Charge Early, Share Publicly

The solo loop: build, ship to paying customers, share the process on X (or wherever the operator's community lives), iterate. Anything that slows this loop is suspect. Shipping is the only forcing function that matters.

### Explicit rejections

Archeia Solo is defined as much by what it refuses as by what it includes:

- **No "hire a team later" assumptions.** The distribution plans as if the operator will remain solo.
- **No PMF interrogation frameworks.** Revenue is the PMF signal. If someone is paying, you have PMF. If nobody is paying, you don't. Rituals don't resolve this.
- **No fundraising logic.** The distribution does not optimize for VC-legible artifacts.
- **No growth-at-all-costs.** Growth must respect bootstrap economics.
- **No sprawling multi-service architectures pretending they're necessary.** If the architecture has more than a handful of containers, `architect` is going to push back.
- **No committee decision processes.** One operator decides.
- **No abstract personas.** Only the operator's own pain and real named buyers count.

A distribution that tried to accommodate both solo builders and VC-backed teams would serve neither. Archeia Solo picks a side.

---

## 7. The forward workflow

Archeia Solo's canonical workflow moves artifacts through the [forward flow](../TEMPORAL_MODEL.md#6-the-forward-flow-product--execution--codebase): `business → product → execution → codebase`.

```
1. Idea strikes
   ↓
2. archeia:clarify-idea
   → writes .archeia/business/drafts/<timestamp>-<slug>.md (shape: transient)
   ↓
3. archeia:create-vision (optional, if the plan needs pressure-testing)
   → updates .archeia/business/vision/vision.md in place (shape: living)
   ↓
4. archeia:review-draft
   → updates .archeia/product/product.md in place (shape: living)
   → writes .archeia/product/decisions/<timestamp>-<slug>.md (shape: accumulating)
   → marks draft as advanced; retention clock starts
   ↓
5. archeia:create  (or  archeia:decompose)
   → reads product.md Features/Constraints/Priorities
   → writes .archeia/execution/projects/<id>.md and
            .archeia/execution/tasks/<id>.md (shape: transient)
   ↓
6. archeia:work + engineer subagent
   → reads the active task
   → writes code in the repo
   → updates task frontmatter through the lifecycle:
       todo → active → done
   ↓
7. Codebase skills re-run (manually or on a schedule)
   → archeia:scan-repo, archeia:scan-git
   → archeia:write-tech-docs, archeia:write-readmes, archeia:write-agents-docs
   → archeia:draw-diagrams
   → all write to .archeia/codebase/ (shape: living, edited in place)
   ↓
8. Shipped.
   → archeia:work marks the task done, records the PR link
   → task enters 14-day retention, then archeia:prune removes it
   → git preserves the task forever
   ↓
9. Repeat from step 1, with the codebase now in its new post-ship state
```

The growth fork runs in parallel:

```
4b. archeia:work (on a growth-domain task)
    → reads .archeia/product/product.md for feature context
    → reads .archeia/business/strategy/strategy.md for pricing/positioning
    → writes .archeia/growth/experiments/<id>.md (shape: transient, running)
    ↓
    Experiment runs.
    ↓
    On conclusion:
      - With learnings: promoted to accumulating record in growth/experiments/
      - Without learnings: enters 7-day retention, then pruned
```

---

## 8. Installation and upgrade

```bash
# Fresh install
git clone https://github.com/Hugopeck/archeia.git ~/.local/share/agent-skills/archeia
cd ~/.local/share/agent-skills/archeia
bash install.sh

# Upgrade (just pull and re-run install.sh; symlinks auto-update from git HEAD)
cd ~/.local/share/agent-skills/archeia
git pull
bash install.sh
```

`install.sh` symlinks:
- All 16 skills into `~/.claude/skills/` (flat namespace, accessible as `archeia:<action>`)
- All agents into `~/.claude/agents/` (personal scope, available in every repo)

Symlinks mean `git pull` immediately updates installed skills and agents — no re-install step required after the first one.

---

## 9. Initializing a new project with Archeia Solo

Once installed, in any repo:

```
# Let an agent do the init (eventually archeia:init)
"Initialize Archeia for this project."
```

Or manually:

```bash
mkdir -p .archeia/{business/{drafts,vision,strategy,landscape},product/{design,decisions},codebase/{architecture,standards,diagrams},growth/{channels,experiments,metrics},execution/{tasks,projects,plans,retros}}
touch .archeia/business/vision/vision.md .archeia/business/strategy/strategy.md .archeia/product/product.md .archeia/growth/metrics/current.md
```

Once the tree exists, start with `archeia:clarify-idea` to capture the first business draft, then follow the forward workflow in §7.

---

## 10. What's pending in Solo 1.0

Honest disclosure of the gaps in the current reference implementation:

- **No explicit `archeia:init`.** Project scaffolding is manual or handled ad-hoc by `archeia:setup-track`. A dedicated `archeia:init` skill is planned for 1.1.
- **No explicit `archeia:validate`.** Schema enforcement is currently social (skills try to follow the contracts, no validator walks the tree). A validator skill is planned for 1.1.
- **No `archeia:prune`.** Retention windows are defined in this document but no pruning skill exists yet. Operators clean up manually or leave old tasks in place.
- **No `archivist` agent.** The inherent agent required by the kernel is not shipped. Planned for 1.1.
- **No `business-skills` owner separation.** `business/` is owned by `product-skills` pending a split.
- **`archeia:todo` is pending.** Requires the bash enforcement layer from the track archive to be backported.
- **Growth domain skills are not shipped.** Only the schema stubs exist. The actual growth workflow is pending.

These gaps are documented here rather than hidden because adopters deserve to know what's production-ready and what's scaffold.

---

## 11. References

- **[`../KERNEL.md`](../KERNEL.md)** — the abstract substrate Solo extends
- **[`../SCHEMA.md`](../SCHEMA.md)** — the canonical five-domain software layout
- **[`../PRINCIPLES.md`](../PRINCIPLES.md)** — the six fundamental truths
- **[`../TEMPORAL_MODEL.md`](../TEMPORAL_MODEL.md)** — the three lifecycle shapes
- **[`../../skills/`](../../skills/)** — the 16 skill implementations
- **[`../../agents/`](../../agents/)** — the personal agent roster
- **[`../../install.sh`](../../install.sh)** — the symlink installer
- **[Claude Code skill docs](https://code.claude.com/docs/en/skills)**
- **[Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents)**
