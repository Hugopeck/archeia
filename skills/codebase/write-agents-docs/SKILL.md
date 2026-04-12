---
name: write-agents-docs
version: 0.0.1
description: |
  Generate colocated agents.md files for directories that need local agent
  orientation. Reads existing READMEs (from archeia:write-readmes) and
  .archeia/ docs to identify directories with locally distinctive rules,
  then creates agents.md + companion claude.md pairs. Does not generate
  root agents.md — only interior colocated files. Requires
  archeia:write-readmes to have been run first (READMEs must exist). Use
  this skill when the user wants to add agent instructions to their
  codebase, improve agent orientation across directories, or ensure agents
  don't make local mistakes from missing context.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Edit
  - Write
---

## Purpose

This skill generates colocated agents.md files — terse, imperative
instruction files that live next to the code they govern. Each agents.md
gives an AI coding agent the local context it needs to avoid mistakes that
someone familiar with that directory would never make.

Read `references/AGENTS_PROTOCOL.md` before starting. It explains the
philosophy behind this skill: the orientation problem, the specificity
principle, the line between READMEs and agents.md, and the CLAUDE.md
bridge rule.

agents.md files are the rules layer. READMEs are the knowledge layer.
They never overlap. The README tells the story — what's here, how it's
organized, what was tried and failed. The agents.md extracts the
imperatives from that story — do this, don't do that, amounts are cents,
handlers must be idempotent. If you find yourself writing narrative or
explanation, stop — that belongs in the README.

This skill does not generate root agents.md (that's a project-wide concern
handled by archeia:write-tech-docs). It generates the interior agents.md
files — the ones that provide local orientation where the root file's
universal rules aren't enough.

## Prerequisites

**archeia:write-readmes must have been run first.** This skill reads
existing READMEs to understand each directory's context, accumulated
learnings, and domain concepts. Without READMEs, you're guessing at what
rules matter — the READMEs contain the knowledge from which rules are
extracted.

If READMEs don't exist, stop and tell the user: "Run archeia:write-readmes
first — agents.md files are the rules extracted from README knowledge, and
the READMEs need to exist first."

## Workflow

### Phase 1: Survey the Landscape

Build a picture of what exists and what needs agents.md files.

1. Read `.archeia/codebase/scan-report.md` if it exists — for the directory listing
   and module structure.

2. Find all existing READMEs in the repo:
   ```
   Glob: **/README.md
   ```
   These are your candidate directories. Every directory with a README is a
   candidate for an agents.md — but most will be filtered out.

3. Find any existing agents.md files:
   ```
   Glob: **/agents.md
   ```
   These will be updated, not replaced.

4. Read the root agents.md if it exists — you need to know what's already
   covered at the project level so you never repeat it.

5. Read `.archeia/codebase/architecture/architecture.md` if it exists — for module boundaries
   and system topology.

6. Read `.archeia/codebase/standards/standards.md` if it exists — for project-wide
   conventions. You need to know these so you can identify where a
   directory *diverges* from them.

7. Read `.archeia/codebase/architecture/dataflow.json` if it exists — for primary request paths
   and integration boundaries. This file is conditional in
   `archeia:write-tech-docs`; its absence is normal and should not be
   treated as a gap.

### Phase 2: Identify Which Directories Need agents.md

Not every directory with a README needs an agents.md. Most don't.

For each directory with a README, apply the specificity test:

**Does this directory have local imperative rules that would prevent an
agent from making a mistake?** Specifically:

- Does it have local invariants that differ from project-wide conventions?
  (amounts in cents, UUIDs not ints, mandatory timestamp formats)
- Does it contain generated files that agents should not hand-edit?
- Does it have module boundary rules? (only talks to X and Y, never
  import from Z directly)
- Does it have local testing requirements that differ from root?
  (special env vars, different test runner, longer timeouts)
- Does it have load-bearing files that agents must not rename or
  restructure?
- Does it have local domain vocabulary where terms mean specific things?
- Does it override project-wide conventions intentionally?

If the answer to any of these is yes, the directory needs an agents.md.
If the parent's agents.md already covers the rules, skip it.

**Read the README first.** The README's Learnings section is the richest
source of agents.md rules. A learning like "Tried converting tasks.py to
async — Django ORM blocks the event loop" becomes the agents.md rule:
"Do not use async in this module. The ORM blocks the event loop."

**Read 2–3 source files** in each candidate directory. Look for:
- Non-obvious patterns (custom base classes, special decorators, wrapper
  types that must always be used)
- Generated code markers (auto-generated headers, codegen config files)
- External service integrations (API clients, webhook handlers)
- Files with high import counts (load-bearing modules)

**Produce a candidate list** before writing anything. Print it for the
user:

```
Directories that need agents.md:

  billing/           — cents not dollars, Stripe-only integration, event bus rule
  billing/webhooks/  — idempotency requirement, STRIPE_TEST_KEY for tests
  auth/              — UUID user IDs, revoke() convention, OAuth provider pattern
  schemas/           — all files generated, do not hand-edit
  api/v2/            — contractual surface, different error format from v1

Directories skipped (no locally distinctive rules):
  billing/models/    — covered by billing/agents.md
  billing/admin/     — no local rules
  auth/migrations/   — no local rules beyond standard migration handling
  api/v2/users/      — covered by api/v2/agents.md
```

### Phase 3: Generate or Update agents.md Files

For each directory from the candidate list:

**Step 1 — Read the directory's README.** This is mandatory. The README
contains the accumulated knowledge from which you extract rules. Pay
special attention to:
- The Learnings section — each learning may become a rule
- Key Concepts — domain vocabulary that agents must use correctly
- Usage — module boundaries and integration points

**Step 2 — Read the root agents.md** (if you haven't already). Verify
that every rule you're about to write is NOT already stated there. If it
is, skip it. Repetition is pollution.

**Step 3 — Read the parent agents.md** (if one exists). Same check —
don't repeat rules the parent already covers.

**Step 4 — Decide: create or update.**

- **No agents.md exists** → create one following the writing rules below.
- **agents.md exists** → read it. Update: add missing rules, refresh
  outdated ones. Never delete rules unless you have evidence they're
  wrong — they may encode constraints you don't see in the code.

**Step 5 — Write the agents.md.**

Every agents.md should include:

1. The locally specific rules discovered during inspection. Group by
   category only if there are 5+ rules — otherwise a flat list is fine.

2. README maintenance scope — explicitly state which READMEs this
   agents.md maintains and the read-before/write-after rules:

```markdown
## README Maintenance

Before working in this directory or its children, read the README.md.
After completing work, update the README's Learnings section with
anything non-obvious you discovered.

Maintains: billing/README.md, billing/models/README.md
```

**Step 6 — Create the companion claude.md.**

In the same directory as the agents.md, create a claude.md with:

```markdown
See [agents.md](agents.md) for local instructions.
```

That's it. No other content unless there are Claude-specific needs at this
directory level (rare).

If a claude.md already exists with substantive content, do not overwrite
it. Instead, ensure it references agents.md and move any imperative rules
from claude.md into agents.md.

### Phase 4: Self-Validation

After generating all agents.md files, validate:

**Step 1 — Specificity check.** Re-read each generated agents.md. For
every rule, ask: "Is this true only in this directory, or is it true
project-wide?" If it's project-wide, delete it. It belongs in root
agents.md.

**Step 2 — Overlap check.** Compare each agents.md against its
directory's README. If any sentence appears in both files in the same
form, remove it from the agents.md and rephrase as an imperative, or
remove it entirely if the README covers it adequately as knowledge.

**Step 3 — Parent repetition check.** Compare each agents.md against its
parent's agents.md (if one exists). Remove any rules that are already
stated in the parent.

**Step 4 — Line count check.** Each agents.md should be 15–40 lines.
Under 15: consider whether the file is needed at all (maybe the parent
covers it). Over 40: you're probably repeating root content or explaining
architecture — trim.

### Phase 5: Report

After processing all directories, print a summary:

```
agents.md generation complete.

Created: 3
  - billing/agents.md (+ claude.md)
  - billing/webhooks/agents.md (+ claude.md)
  - auth/agents.md (+ claude.md)

Updated: 1
  - api/v2/agents.md (added contractual surface rules)

Skipped (no local rules): 8
  - billing/models/, billing/admin/, auth/migrations/, ...

README maintenance assignments:
  - billing/agents.md → billing/README.md, billing/models/README.md
  - billing/webhooks/agents.md → billing/webhooks/README.md, billing/webhooks/schemas/README.md
  - auth/agents.md → auth/README.md
```

## Writing Rules

These are the rules for what goes INTO the agents.md files this skill
generates. They come from the AGENTS_PROTOCOL.md.

- **Imperative, not explanatory.** "All amounts are cents" not "We chose
  to represent amounts as cents because..." If you're writing narrative,
  it belongs in the README.
- **Terse.** Each rule: 1–2 lines. If it takes a paragraph, it belongs
  in the README or Architecture.md.
- **Flat.** No heading hierarchy deeper than H2. Flat lists of rules.
- **15–40 lines.** Under 15: probably don't need the file. Over 40:
  repeating root content or explaining architecture.
- **Concrete values.** "Timeout is 120s" not "timeout is longer than
  default." Name the files, name the env vars, name the commands.
- **Always include README maintenance scope.** State which READMEs this
  agents.md maintains and the read-before/write-after rules.

## Quality Rules

- **The specificity test.** Every rule must be locally specific — true
  only in this directory or different from the project-wide default. If
  it would apply identically in 5+ directories, it belongs in root
  agents.md.
- **No overlap with README.** The README describes and accumulates
  knowledge. The agents.md instructs. Same sentence in both = one of them
  is wrong.
- **No repetition from root.** If root agents.md says it, don't repeat
  it. Repetition is pollution.
- **No repetition from parent.** If a parent agents.md says it, don't
  repeat it. The agent reads both.
- **Evidence-grounded.** Every rule must be verifiable by reading the
  directory's code or its README's Learnings section. Do not invent
  constraints.
- **Companion claude.md is mandatory.** Every agents.md gets a claude.md.
  No exceptions. Thin pointer only.
- **Preserve existing rules.** When updating, never delete rules unless
  you have evidence they're wrong. They may encode constraints invisible
  to code inspection.

## Anti-Patterns

- **The mini root agents.md.** An agents.md that restates project-wide
  setup commands, tech stack, or code style. These are root concerns.
- **The narrative agents.md.** An agents.md that explains history,
  rationale, or architecture. That's the README's job.
- **The exhaustive agents.md.** An agents.md with 80+ lines covering
  every possible scenario. Keep it to what an agent would get wrong.
- **The duplicator.** Same content in agents.md and README.md. Pick one.
- **Missing claude.md.** An agents.md without its companion. Claude will
  never see it.
- **The chain.** agents.md at every depth level (api/agents.md,
  api/v2/agents.md, api/v2/users/agents.md, api/v2/users/prefs/agents.md).
  Most of these are unnecessary — the parent covers the children.

## Expected Output

For each directory identified as needing local agent orientation:
- One `agents.md` (15–40 lines of imperative rules)
- One `claude.md` (thin pointer to agents.md)

Files are written directly into each directory.
