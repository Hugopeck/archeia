# The README Protocol

A protocol for writing and maintaining READMEs in the agentic era.

---

## The Shift

For decades the README was the only file that greeted you when you opened a
repository. It carried everything: what the project does, how to install it,
coding standards, contribution guidelines, architecture notes, badges, license
text, troubleshooting, and whatever else seemed important at the time. It was
a single document trying to serve every reader — new hires, evaluators,
contributors, operators, and eventually AI coding agents.

That era is over.

Today a repository speaks through multiple specialized files. `CLAUDE.md` and
`AGENTS.md` give AI agents the imperative rules they need. `Guide.md` holds
setup and operational commands. `Standards.md` codifies conventions.
`Architecture.md` maps the system. Skills automate generation and maintenance.
The README no longer needs to carry all of that — and it shouldn't.

When a README tries to serve both humans and machines, it serves neither well.
Agents choke on vision statements and badge walls. Humans glaze over pages of
CLI flags and linting rules. The fix is separation of concerns: let each file
do what it does best.

**README = Knowledge.** It answers: *What is this, how does it work, and
what has been learned here?*

A README is the institutional memory of a directory. It describes what's
here and how it's organized — but it also accumulates learnings over time:
tried approaches that failed, gotchas discovered during development, dead
ends that shouldn't be revisited. This accumulated knowledge is what makes
READMEs valuable to both humans and agents — not as instructions, but as
context that prevents repeating mistakes.

Imperative rules for agents — do this, don't do that — belong in
`agents.md`. The README tells the story; `agents.md` extracts the rules.

Everything else has a better home.

---

## Why Colocate

Traditional repos put one README at the root and call it done. Deeper
directories — the ones where developers actually spend their time — go
undocumented. A new contributor lands in `src/services/billing/` and has to
reverse-engineer what it does from import statements and variable names.

Colocated READMEs fix this. A README lives next to the code it describes, at
whatever directory level makes sense. The benefits:

- **Discoverability.** You open a directory, the README is right there. No
  hunting through a central docs/ folder or searching a wiki.
- **Maintenance proximity.** When the code in a directory changes, the README
  is in the same diff. Reviewers can see when docs drift from reality.
- **Scales with the codebase.** As the project grows and directories multiply,
  documentation grows with it — each directory responsible for its own context.
- **AI-friendly.** An agent working in a directory can read its README for
  local context without loading the entire project's documentation.

The root README is special — it's the project's front door and carries brand,
identity, and first impression. This skill does not generate root READMEs
because they are personal and project-specific. It generates the interior
READMEs — the ones that make a codebase navigable.

---

## What Goes In

A colocated README answers five questions:

### 1. What is this?

The directory name is often cryptic (`lib/`, `services/`, `middleware/`). The
README gives it meaning: what this module does, what role it plays in the
larger system, and who cares about it.

One paragraph. No marketing language. Evidence from the actual code.

### 2. How is it organized?

A mermaid diagram or annotated tree showing internal structure. Humans are
spatial thinkers — a visual map orients faster than paragraphs of prose.

Mermaid diagrams are first-class here because they are:
- **Diffable** — they're text, so changes show up in code review
- **Colocated** — no separate image files to get out of sync
- **Renderable everywhere** — GitHub, GitLab, VS Code, most doc tools
- **No build step** — unlike generated PNGs or SVGs

Keep diagrams to 10 nodes max. This is an overview, not a schematic.

### 3. What are the key concepts?

The 3–5 things you need to understand before working in this directory.
Patterns, abstractions, conventions, or domain terms that aren't obvious from
file names. This is the section that saves a developer 30 minutes of
code-reading.

### 4. How is it used?

How other parts of the codebase consume this module. Import patterns, public
API surface, integration points. This tells you what will break if you change
something here.

### 5. What has been learned?

This is the section that matters most over time. Tried approaches that
failed, dead ends that shouldn't be revisited, constraints discovered
during development, gotchas that aren't obvious from reading the code.

This section is different from the others. It's not generated from code
analysis — it accumulates organically as people and agents work in the
directory. An empty section is fine at creation time. Its value grows
with every contribution.

A developer who spent two days debugging a race condition in the webhook
handler writes it here. An agent that tried refactoring to async and
discovered the ORM doesn't support it writes it here. The next person
who opens this directory reads it and skips those dead ends.

This is the README's most important function in the agentic era: agents
work in short sessions, and without this section, every session starts
from zero. With it, each session builds on the last.

---

## What Stays Out

Everything that has a better home elsewhere:

| Content | Where it belongs | Why not the README |
|---------|-----------------|-------------------|
| Setup and install instructions | `Guide.md` / `.archeia/codebase/guide.md` | Operational, not educational. Changes with tooling, not with code. |
| Coding standards and conventions | `Standards.md` / `.archeia/codebase/standards/standards.md` | Rules for agents and linters to enforce, not for humans to memorize. |
| Agent imperatives (do/don't rules) | Colocated `agents.md` | Commands belong in agents.md. The README describes and accumulates knowledge; agents.md instructs. |
| System architecture and data flow | `Architecture.md` / `.archeia/codebase/architecture/architecture.md` | Cross-cutting concern, not scoped to one directory. |
| API reference documentation | Generated docs / code comments | Changes with every function signature. Automate, don't hand-write. |
| Badges and shields | Nowhere | Noise. A CI badge tells you nothing a failed build notification doesn't. |
| License text | `LICENSE` file | One file at the root. Subdirectories inherit. |
| Contribution guidelines | `CONTRIBUTING.md` | One file at the root. Link if needed. |
| Verbose changelogs | `CHANGELOG.md` / git history | `git log` is the source of truth. |
| Technology marketing | Nowhere | "Modern, scalable, blazing fast" tells you nothing. State what it does. |

The principle: if content is better maintained by automation, enforced by
tooling, or scoped to a different audience, it does not belong in the README.

---

## README and agents.md

A directory can have both a README.md and an `agents.md`. They are
complementary — the knowledge layer and the rules layer — and they must
never overlap.

**README.md** is descriptive and narrative. It tells you what's here, how
it works, what was tried, what failed. It's for humans and agents to
*read* — to build understanding before acting. Its tone is informational.

**agents.md** is imperative and terse. It tells agents what to do and what
not to do. It's extracted from the knowledge in the README but stripped of
narrative. Its tone is commanding.

The README says: "We handle Stripe webhooks here. The event processing
pipeline retries up to 3 times with exponential backoff. We tried using a
queue-based approach in Q3 2024 but reverted because webhook ordering
guarantees were lost (see PR #847)."

The agents.md says: "Handlers must be idempotent. Amounts are cents. Do not
refactor to queue-based processing."

If the same sentence appears in both files, ask which form it belongs in.
A fact or narrative → README. A command → agents.md.

Not every directory needs an `agents.md` — most don't. But every directory
with an `agents.md` is responsible for maintaining the READMEs in its scope.
See the Colocated AGENTS.md Protocol for the full system.

---

## Updating READMEs in the Agentic Era

The old problem with colocated READMEs was maintenance. Writing them was easy;
keeping them current was not. Developers changed code but forgot to update
the README two tabs over. Over time, READMEs drifted into fiction.

AI agents eliminate this problem. An agent can:
- Detect when a directory's structure has changed
- Read the current README and compare it against reality
- Update structural sections (organization, usage) automatically
- Flag conceptual sections for human review when the code's intent shifts

This changes the maintenance model:

**AI maintains structure.** The organization diagram, file listings, import
patterns, and usage examples can be regenerated from code analysis. Let agents
do this — they won't forget, and they won't get it wrong.

**Humans maintain meaning.** The "what is this" paragraph, the key concepts,
the domain explanations — these require understanding of intent that lives in
people's heads, not in the code. Humans write these sections; agents preserve
them across updates.

**The update cycle:**
1. `archeia:scan-repo` identifies which directories need READMEs
2. `archeia:write-readmes` creates or updates them
3. Structural sections are regenerated from current code
4. Human-written content is preserved — never overwritten
5. Stale sections are flagged, not silently replaced

This means READMEs can exist everywhere without becoming a maintenance burden.
A repo with 50 directories can have 50 READMEs, each kept current by the same
agents that write the code.

**Everyday knowledge accumulation.** Beyond the archeia skill cycle,
READMEs grow through normal work. When an agent fixes a bug, adds a
feature, or refactors code in a directory — and discovers something
non-obvious — it should add that learning to the README's "What has been
learned?" section.

The colocated `agents.md` (if one exists) instructs agents to read the
README before planning and update it after completing work. This turns
every agent session into a knowledge contribution. Over time, the learnings
section becomes the most valuable part of the README — a persistent record
of tried approaches, dead ends, and hard-won context that no single session
would produce.

**Learnings are sacred.** When updating a README, never delete, summarize,
or "clean up" accumulated learnings. Every entry was written by someone —
human or agent — who discovered something the hard way. Append only.

---

## Design Decisions

### Mermaid over images

External image files (`docs/images/architecture.png`) rot. They require a
separate tool to edit, a build step to generate, and a human to remember to
update them. Mermaid diagrams are text that lives in the markdown file. They
render natively on GitHub and GitLab. They show up in diffs. An agent can
update them without image-editing tools.

### Max 40 lines (excluding mermaid)

A README that requires scrolling has failed. Forty lines forces discipline: if
you can't explain a directory in 40 lines, either the directory does too much
or you're including content that belongs elsewhere. The mermaid exemption
exists because diagrams are dense information — a 15-node diagram replaces
paragraphs of prose.

### No root README generation

The root README is a project's identity. It carries brand, personality, first
impressions, and often serves audiences beyond developers (recruiters,
evaluators, users, investors). Generating this from code analysis strips away
everything that makes it human. This skill generates the interior READMEs —
the utilitarian ones that make a codebase navigable — and leaves the front
door to the humans who know what their project means.

### Create or update, never delete

When a README already exists, the skill updates it — adding missing sections,
refreshing structural content — but never removes human-written content. Even
if a section seems outdated, preservation is safer than deletion. The skill
flags staleness; humans decide what to cut.

### README as knowledge accumulator

READMEs in the agentic era serve a function they never had before: they
are the persistent memory across ephemeral agent sessions. An agent works
for an hour, discovers that the billing module can't use async because the
ORM blocks, and moves on. Without recording that learning, the next agent
session will try async again, hit the same wall, and waste the same hour.

The "What has been learned?" section solves this. It turns READMEs from
static documentation into living knowledge bases that grow smarter with
every session. This is why learnings are append-only — each entry
represents work that doesn't need to be repeated.

### Drawing from established practices, adapted

This protocol draws from:
- **Diátaxis** — the distinction between explanation (README) and how-to
  guides (Guide.md) comes directly from Diátaxis's four documentation modes
- **C4 Model** — mermaid diagrams follow C4's progressive zoom philosophy,
  scoped to the directory's level of abstraction
- **GitHub Docs style** — concise, scannable, no filler words
- **Open Source Guides** — the principle that good docs lower the barrier to
  contribution

What we leave behind:
- **Badge culture** — badges were a proxy for project health when CI dashboards
  weren't universal. They are now visual noise.
- **All-in-one READMEs** — the monolithic README was necessary when it was the
  only documentation file. It is no longer the only file.
- **Technology lists** — "Built with React, TypeScript, Tailwind, PostgreSQL"
  tells you what `package.json` already tells you. State what the project does,
  not what it's made of.
- **Verbose getting-started guides** — these belong in Guide.md where agents
  and humans can find operational instructions in a predictable location.
