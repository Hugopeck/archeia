# Archeia Solo — Reference Distribution of the Archeia Standard

This repository is **Archeia Solo**, the canonical software reference implementation of the [Archeia Standard](https://github.com/Hugopeck/archeia-standard). The open spec lives upstream; this repo contains the skills, agents, and tooling that implement the Solo distribution for solo builders shipping bootstrapped AI-first software products.

If you want to understand the standard, read it upstream. If you want to adopt the standard as a solo operator, install this repo.

## Install

```bash
git clone https://github.com/Hugopeck/archeia.git ~/.local/share/agent-skills/archeia
bash ~/.local/share/agent-skills/archeia/install.sh
```

`install.sh` symlinks every skill under `skills/<domain>/<name>/` into `~/.claude/skills/` and every agent under `agents/*.md` into `~/.claude/agents/`. Symlinks mean a `git pull` here immediately updates the installed skills and agents with no re-install step.

## What's in this repo

- **[`DISTRIBUTION.md`](DISTRIBUTION.md)** — the Solo distribution spec. Audience, kernel conformance, skill roster, agent roster, status vocabularies, retention windows, ethos, forward workflow, install, and pending-work disclosure. This is the canonical description of what Archeia Solo is and is not.
- **`skills/`** — 16 skills organized by domain:
  - `skills/product/` — `clarify-idea`, `create-vision`, `review-draft`, `lock-spec`
  - `skills/codebase/` — `scan-repo`, `scan-git`, `write-tech-docs`, `write-readmes`, `write-agents-docs`, `draw-diagrams`
  - `skills/execution/` — `work`, `create`, `decompose`, `setup-track`, `todo`, `update-track`
  - `skills/business/` — reserved (per the standard)
  - `skills/growth/` — reserved (per the standard)
- **`agents/`** — personal Claude Code subagents (`architect`, `engineer`) that install to `~/.claude/agents/` and are available in every repo you open, not just Archeia ones.
- **`evals/`** — the codebase-domain eval harness plus the smoke test suite (`evals/smoke/`) that verifies the harness and skill integration.

## The upstream spec

All structural claims and contracts come from [github.com/Hugopeck/archeia-standard](https://github.com/Hugopeck/archeia-standard). The key documents there:

- **[MANIFESTO.md](https://github.com/Hugopeck/archeia-standard/blob/main/MANIFESTO.md)** — the one-page pitch
- **[PRINCIPLES.md](https://github.com/Hugopeck/archeia-standard/blob/main/PRINCIPLES.md)** — the seven fundamental truths
- **[KERNEL.md](https://github.com/Hugopeck/archeia-standard/blob/main/KERNEL.md)** — the formal substrate: primitives, invariants, operations, inherent skills
- **[SCHEMA.md](https://github.com/Hugopeck/archeia-standard/blob/main/SCHEMA.md)** — the canonical software application of the kernel (five domains, three contracts)
- **[TEMPORAL_MODEL.md](https://github.com/Hugopeck/archeia-standard/blob/main/TEMPORAL_MODEL.md)** — the three lifecycle shapes
- **[ONTOLOGY.md](https://github.com/Hugopeck/archeia-standard/blob/main/ONTOLOGY.md)** — canonical vocabulary grounded in cognitive science and recent AI research
- **[docs/memory-vs-knowledge.md](https://github.com/Hugopeck/archeia-standard/blob/main/docs/memory-vs-knowledge.md)** — the honest audit of what Archeia solves and what it doesn't

## Why the split

The Archeia Standard defines a kernel that distributions extend. Keeping the kernel inside one specific distribution's repo (Solo) contradicted the spec's own architectural claim. The split (completed 2026-04-13) positions future distributions (Research, Studio, Enterprise) as peers of Solo rather than children of it, and gives the standard an independent URL that can be cited without depending on any one distribution's repo layout.

Prior history of the standard files lives in this repo under `git log --follow standard/<file>` for commits up through `e037dc8`. Going forward, standard-level changes happen upstream in `archeia-standard`; Solo-specific changes happen here.

## License

MIT.
