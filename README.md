# Archeia

**A standard for organizing project knowledge inside software repositories.**

The spec lives at [`standard/SCHEMA.md`](standard/SCHEMA.md). This repo is the reference implementation.

## The Problem

Architecture knowledge lives in a senior dev's head. Product decisions live in Notion. Business strategy lives in a founder's pitch deck. Growth experiments live in a spreadsheet. Task state lives in Jira. None of it lives where agents can see it — next to the code.

AI agents compensate by reading file names, inferring structure, and guessing. They get the topology wrong because the topology was never written down in a place they could find. When agents do produce documentation, there's no standard for where it goes, who owns it, or what format it takes. Every project reinvents this from scratch.

## The Standard

Archeia defines a canonical location (`.archeia/`), a fixed set of domains, clear ownership per domain, and contracts for cross-domain reads. The five domains:

| Domain | Purpose | Owner |
|---|---|---|
| `business/` | Why we're building, for whom, how we make money | Business skills |
| `product/` | Locked, implementation-ready spec | Product skills |
| `codebase/` | What the code is right now (descriptive, regenerable) | Codebase skills |
| `growth/` | How we acquire, retain, monetize | Growth skills |
| `execution/` | What we're doing right now | Execution skills |

Each domain is independent. A project might use only some of them. Full details in [`standard/SCHEMA.md`](standard/SCHEMA.md).

## Reference Implementation

This repo ships skills organized by domain. Each skill is a `SKILL.md` file containing YAML frontmatter plus a prompt/workflow:

```
skills/
├── product/            # Product-domain skills (from former hstack)
│   ├── clarify-idea
│   └── create-vision
├── codebase/           # Codebase-domain skills (the former archeia pipeline)
│   ├── scan-repo
│   ├── scan-git
│   ├── write-tech-docs
│   ├── write-readmes
│   ├── write-agents-docs
│   └── draw-diagrams
└── execution/          # Execution-domain skills (from former track)
    ├── work
    ├── create
    ├── decompose
    ├── setup-track
    ├── todo
    └── update-track
```

Skills install under the `archeia:` namespace — e.g. `archeia:scan-repo`, `archeia:clarify-idea`, `archeia:work`. Not every project needs every skill.

## Installation

```bash
git clone https://github.com/Hugopeck/archeia.git ~/.local/share/agent-skills/archeia
bash ~/.local/share/agent-skills/archeia/install.sh
```

## Built On

- [C4 Model](https://c4model.com/) — Three-level architecture zoom driving `codebase/architecture/*.json`
- [arc42](https://arc42.org/overview) — Architecture documentation template
- [Diataxis](https://docs.diataxis.fr/) — Separation of reference, how-to, explanation, tutorial
- [Docs as Code](https://www.docops.io/docs-as-code/) — Documentation lives in the repo
- [agents.md](https://www.agents.md/) — Open standard for agent-readable docs
- [ADR](https://adr.github.io/) — Decision capture format used in `product/decisions/`

## License

MIT
