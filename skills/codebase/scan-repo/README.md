# archeia:scan-repo

Entry-point skill for the archeia documentation pipeline. Scans a repository
and produces a quantitative metrics report — answering "how big is this repo,
what's in it, and where are the gaps?" in under 30 seconds of reading.

Run this first, before `archeia:write-tech-docs` or `archeia:write-readmes`.

## What it produces

`.archeia/codebase/scan-report.md` — a single document with:

| Section | What it measures |
|---------|-----------------|
| Size | LOC by language (via `wc -l` or `tokei`/`cloc`) |
| Token Estimates | Approximate token count per top-level directory (bytes / 4) |
| Structure | Directory tree to depth 2 with file counts |
| Modules | Workspace members, packages, or top-level source directories |
| README Coverage | Which directories have READMEs and which need them |
| Dependencies | Direct and dev dependency counts per manifest |
| Test Footprint | Test file count, source file count, coverage ratio |
| Git Vitals | Repo age, total commits, contributors, last commit, branch count |
| Signals | CI workflows, Docker services, TODO/FIXME density, entry points, large files |

## Key Concepts

- **Quantitative only** — this skill counts and measures. It does not interpret
  architecture, describe what modules do, or prescribe standards. That boundary
  belongs to `archeia:write-tech-docs`.
- **README Coverage drives downstream skills** — the coverage table is consumed
  by `archeia:write-readmes` to determine which directories get READMEs.
- **Every number is measured** — no estimates from framework knowledge. LOC
  comes from `wc -l`, commits from `git rev-list`, deps from manifest parsing.

## Usage

Other archeia skills depend on this output:
- `archeia:write-readmes` reads the README Coverage table
- `archeia:write-tech-docs` benefits from the size/structure context
- `archeia:scan-git` can run independently but is typically sequenced after this

## Evals

`evals/` contains runs against real repos: Futuur API (227k LOC Django),
Track (72k LOC Python), and Track App (21k LOC Markdown/Bash).
