# The Colocated AGENTS.md Protocol

A protocol for agent orientation in interior directories.

This protocol covers colocated agents.md files — the ones that live inside
subdirectories, next to the code they govern. It does not cover the root
agents.md, which is a project-wide concern.

---

## The Orientation Problem

An agent arrives in `billing/webhooks/`. It knows the project uses Python,
ruff, pytest — the root agents.md told it that. What it doesn't know:

- Amounts in this module are integer cents. It refactors a function and
  introduces a dollars-to-cents conversion that already happened upstream.
  Tests pass — the fixtures use cents consistently. Production doubles
  every charge.

- An agent working in `schemas/` regenerates a file by hand. That file is
  produced by `scripts/generate_schemas.sh`. The handwritten version drifts
  from the generator's output within a week.

- An agent in `auth/` adds a new OAuth provider. It doesn't implement
  `revoke()` — a local convention that every provider must follow. This
  convention exists nowhere in the project-wide standards because it's
  specific to this module.

These are not capability failures. The agent is competent. It just doesn't
know where it is. A human who has worked in that directory for a week would
never make these mistakes — they have the local context.

The colocated agents.md gives an agent that context in 30 lines.

---

## The Principle of Specificity

One rule determines what belongs in a colocated agents.md:

**If it's true across the whole repo, it belongs in root agents.md. If it's
true only in this directory — or if it differs from the project-wide
default — it belongs in the colocated agents.md.**

This is a filter, not a template. There are no required sections. You don't
fill out a form. You ask: "what's true HERE that isn't true EVERYWHERE?"

A colocated agents.md that repeats root-level instructions has failed.
Repetition between root and colocated files is not reinforcement — it's
pollution. It wastes the agent's context window and trains it to skim past
the distinctive parts.

---

## README and agents.md — The Line

A directory can have both a README.md and an agents.md. They are
complementary halves — the knowledge layer and the rules layer — and they
must never overlap.

**README.md = accumulated knowledge.** Descriptive, narrative, informative.
It's the institutional memory of a directory — what's here, how it's
organized, what was tried and what failed, what approaches were abandoned
and why. It's for humans AND agents to read. The most valuable part of a
README is the accumulated learnings: tried approaches, dead ends, "we tried
X but it didn't work because Y." This is what prevents the next person or
agent from repeating a mistake.

**agents.md = imperatives.** Do this. Don't do that. Terse, instructive,
agents-only. It doesn't explain or narrate — it commands. The rules
extracted from the knowledge in the README, stripped of narrative.

The README says: "We handle Stripe webhooks here. The event processing
pipeline retries up to 3 times with exponential backoff. We tried using a
queue-based approach in Q3 2024 but reverted because webhook ordering
guarantees were lost (see PR #847)."

The agents.md says: "Handlers must be idempotent. Amounts are cents. Do not
refactor to queue-based processing."

The README gives you the story. The agents.md gives you the rules.

If the same sentence appears in both files, ask which form it belongs in.
A fact or narrative → README. A command → agents.md.

---

## agents.md Maintains READMEs

The agents.md owns the README lifecycle in its scope. One agents.md can
maintain multiple READMEs — not every directory with a README needs its own
agents.md, but every agents.md is responsible for the READMEs within its
reach, including child directories that don't have their own agents.md.

**The read-before-work rule.** Before planning or coding in any directory
within scope, read its README. The README contains accumulated knowledge —
tried approaches, dead ends, domain context — that should inform your plan
before you write a line of code.

**The write-after-work rule.** After completing work that changes how a
directory works, or after discovering something non-obvious — a gotcha, a
failed approach, a constraint — update the README with your learnings. The
README is a living document.

This creates a virtuous cycle: agents read READMEs to avoid past mistakes,
and they write to READMEs to prevent future ones. Every agent session
becomes a knowledge contribution.

```
billing/
├── agents.md          ← maintains READMEs for billing/, models/, webhooks/
├── README.md
├── models/
│   └── README.md      ← maintained by billing/agents.md
└── webhooks/
    ├── agents.md      ← takes over: maintains READMEs for webhooks/, schemas/
    ├── README.md
    └── schemas/
        └── README.md  ← maintained by billing/webhooks/agents.md
```

---

## What Goes In

Each category below includes concrete examples from different domains. Not
every agents.md will have all categories — include only what's locally
distinctive.

**Local invariants and constraints.**
- `billing/`: "All monetary amounts are integer cents. Never convert to
  dollars in this module."
- `auth/`: "User IDs are UUIDs, not auto-incrementing integers. All
  comparisons must use string equality."
- `api/v2/`: "All timestamps are ISO 8601 UTC. The `Z` suffix is mandatory.
  Do not use `datetime.now()`."

**Local gotchas and traps.**
- `schemas/`: "Files in this directory are generated by
  `scripts/generate_schemas.sh`. Do not hand-edit. Modify source
  definitions in `schemas/definitions/` and regenerate."
- `billing/webhooks/`: "Webhook handlers must be idempotent. Stripe sends
  duplicate events. Every handler must check for prior processing."
- `migrations/`: "Never rename a migration file. Never reorder. The numeric
  prefix is the execution order."

**Module boundaries as rules.**
- `billing/`: "This module talks to Stripe and PagerDuty. It does NOT
  import from `auth/` or `notifications/` directly — use the event bus."
- `api/v2/`: "This directory is the public API surface. Every endpoint is
  contractual. Do not rename paths or remove fields without a deprecation."

**Local testing requirements.** Only when they differ from root.
- `billing/webhooks/`: "Tests require `STRIPE_TEST_KEY` env var. Run with
  `STRIPE_TEST_KEY=sk_test_xxx pytest billing/webhooks/`."
- `infra/`: "Tests spin up Docker containers. Run `make test-infra` instead
  of plain `pytest`. Timeout is 120s, not the default 30s."

**Load-bearing files.**
- `lib/core/`: "`registry.py` is imported by 40+ modules. Do not rename it
  or change its public interface without updating all consumers."
- `config/`: "`base.py` is the settings file that every other settings file
  inherits from. Changes here affect all environments."

**Local domain vocabulary.**
- `billing/`: "A 'charge' is an attempted payment. A 'payment' is a
  completed charge. These are not synonyms in this module."
- `trading/`: "'Position' means a user's net holdings in one outcome.
  'Wager' means a single transaction. One position is built from many
  wagers."

**Local overrides to project-wide conventions.**
- `legacy/`: "This directory uses `var` instead of `const/let`. Intentional
  — it runs in an environment without ES6 support. Do not modernize."
- `api/v1/`: "Returns `{error: string}`, not the project-wide
  `{errors: [{code, message}]}`. Backwards-compatibility constraint."

**README maintenance scope.**
- Which READMEs this agents.md is responsible for.
- The read-before-work and write-after-work rules for directories in scope.

Every item in a colocated agents.md should be something an agent would get
wrong without it. If an agent would figure it out from reading the code, it
doesn't need to be stated. The file contains the things that are invisible
to code reading — conventions, intentions, historical constraints.

---

## What Stays Out

| Content | Where it belongs | Why not here |
|---------|-----------------|--------------|
| Project-wide setup, build, lint commands | Root agents.md | Universal, not local |
| What this module is, how it's organized | README.md | Knowledge, not commands |
| Tried approaches and dead ends | README.md | Narrative that accumulates over time |
| Architecture diagrams and system maps | `.archeia/codebase/architecture/architecture.md` | Reference, not rules |
| Code style that applies everywhere | Root agents.md / Standards.md | Not directory-specific |
| Historical rationale for decisions | ADRs / Architecture.md | Agents need current rules, not history |
| Anything already stated in root agents.md | Root agents.md | Repetition is pollution |

If you're restating project-wide rules "just in case," stop. The agent
already has those. You're wasting its context window and training it to
skim.

---

## The Depth Problem

Not every directory needs an agents.md. Most don't.

**The heuristic:** Does this directory have local imperative rules that
would prevent an agent from making a mistake? If yes, create one. If the
parent's agents.md covers it, or if there's nothing locally surprising,
skip it.

- `api/` might need one (versioning rules, rate limit conventions).
  `api/v2/` might need one (different response format from v1).
  `api/v2/users/` probably doesn't — the v2 agents.md covers it.
- `billing/` needs one (cents not dollars, Stripe integration rules).
  `billing/models/` probably doesn't. `billing/webhooks/` does
  (idempotency, duplicate handling).
- A chain of agents.md at every depth level is almost certainly wrong.
  Each level should only exist if it has genuinely distinct local context.

Files inherit naturally. An agent working in `billing/webhooks/` reads
both `billing/agents.md` AND `billing/webhooks/agents.md`. The webhook
file should not repeat what the billing file says.

A directory without an agents.md can still have a README. The nearest
parent agents.md maintains it.

Under-documenting is fine. Thin, repetitive agents.md files are worse than
no files at all — they teach agents that these files contain nothing useful.

---

## The CLAUDE.md Bridge Rule

**Every colocated agents.md gets a companion claude.md in the same
directory. No exceptions.**

Claude Code reads claude.md files automatically on startup but does NOT
scan agents.md files. Without the companion, Claude never sees your local
instructions.

The claude.md is always a thin pointer:

```markdown
See [agents.md](agents.md) for local instructions.
```

Add Claude-specific configuration below the pointer only if there are
Claude-specific needs at this directory level. This is rare — most
directory-level claude.md files are just the pointer.

This is not a philosophical decision. It's a compatibility shim. The
substantive content lives in agents.md (vendor-neutral, readable by Codex,
Jules, Cursor, Aider, Copilot, and Claude). The pointer lives in claude.md
(ensuring Claude Code picks it up).

If agents.md doesn't exist in a directory, claude.md shouldn't either.
They're a pair.

---

## Writing Style

- **Imperative, not explanatory.** "All amounts are cents" not "We chose to
  represent amounts as cents because..."
- **Terse.** Each rule should be 1–2 lines. If it takes a paragraph to
  explain, it belongs in the README or Architecture.md.
- **Flat.** No heading hierarchy deeper than H2. These are lists of local
  rules, not structured documents.
- **15–40 lines.** Under 15 and you probably don't need the file. Over 40
  and you're repeating root content or explaining architecture.
- **Concrete values.** "Timeout is 120s" not "timeout is longer than
  default." Name the files, name the env vars, name the commands.
- **Include the README rules.** Every agents.md should explicitly state the
  read-before-work and write-after-work rules for its scope.

---

## Design Decisions

**agents.md over vendor-specific files as canonical.** The agents.md spec
is vendor-neutral, adopted by 60,000+ projects, and readable by every
major AI coding tool. Putting substantive content in claude.md or
`.cursor/rules` makes it invisible to everything else. Write once in
agents.md, bridge to vendor formats.

**No root agents.md generation.** Root agents.md is a project-wide concern
handled separately. This protocol is exclusively for interior files — the
ones that provide local orientation where the root file's universal rules
aren't enough.

**Filter over template.** Unlike the README Protocol which has five
standard sections, colocated agents.md has no required sections. You
include what's locally distinctive and nothing else. A file with one rule
is valid. A file with seven categories is valid. Shape follows content.

**README as knowledge accumulator, agents.md as rules.** READMEs grow over
time as agents and humans contribute learnings — tried approaches, dead
ends, hard-won context. agents.md stays terse and stable. The README is the
memory; agents.md is the rulebook. They are complementary and never overlap.

**The specificity test is the only test.** Every decision in this protocol
derives from one question: is this locally specific? If yes, include. If
no, omit. This keeps the protocol simple enough to internalize.

This protocol draws from the [agents.md](https://www.agents.md/) open
standard, [Anthropic's CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory)
documentation, and the README Protocol's separation-of-concerns philosophy.
