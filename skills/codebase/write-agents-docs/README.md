# archeia:write-agents-docs

A skill that generates colocated agents.md files across a repository so every directory with locally distinctive rules has terse, imperative agent orientation next to its code.

## What it does

Reads existing READMEs (from `archeia:write-readmes`) and `.archeia/` docs to identify directories where agents would make mistakes without local context, then creates `agents.md` + companion `claude.md` pairs in each one.

Each generated agents.md contains only what's locally specific:
- **Local invariants** — amounts in cents, UUIDs not ints, mandatory timestamp formats
- **Local gotchas** — generated files, idempotency requirements, order-dependent operations
- **Module boundaries** — what this directory talks to and what it must not import
- **Local testing** — env vars, different runners, longer timeouts
- **Load-bearing files** — modules too widely imported to rename
- **Domain vocabulary** — terms that mean specific things in this directory
- **README maintenance scope** — which READMEs this agents.md maintains

## What it doesn't do

- Generate a root agents.md (project-wide, handled by archeia:write-tech-docs)
- Repeat anything from root agents.md or parent agents.md
- Write narrative or explanation (that's the README's job)
- Create agents.md for directories without locally distinctive rules

## Prerequisites

Run `archeia:write-readmes` first. This skill reads READMEs — especially their Learnings sections — to extract the imperative rules that belong in agents.md.

## Philosophy

See `references/AGENTS_PROTOCOL.md` for the full protocol — the orientation problem, the specificity principle, the line between READMEs and agents.md, the CLAUDE.md bridge rule, and the depth heuristic.
