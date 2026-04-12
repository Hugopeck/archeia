# archeia:scan-git

Analyzes git history to produce a team collaboration and dynamics report —
answering "who builds this and how do they work together?" Sits between
`archeia:scan-repo` (codebase metrics) and `archeia:write-tech-docs`
(architecture interpretation) in the pipeline.

## What it produces

`.archeia/codebase/git-report.md` — a single document with:

| Section | What it measures |
|---------|-----------------|
| Contributor Roster | Active/inactive contributors, first/last commit dates, commit counts |
| Integration Patterns | Who merges code, merge-to-commit ratios, PR review patterns |
| Collaboration Density | Co-authorship frequency, cross-module contributions, pair patterns |
| Knowledge Flow | Which contributors work across which modules, knowledge silos |
| Velocity | Commits per week/month trends, acceleration/deceleration |
| Churn | Lines added/removed ratios, high-churn files and directories |
| Time Patterns | Commit activity by day-of-week and hour, timezone distribution |
| Bus Factor | Per-directory ownership concentration, single-contributor risk areas |
| Revert & Rework | Revert frequency, fixup chains, files with high rework rates |

## Key Concepts

- **Collaboration-first** — the core sections (Integration Patterns,
  Collaboration Density, Knowledge Flow, Revert & Rework) cover ground that
  standard git analysis tools don't. The lightweight sections (Velocity, Churn,
  Bus Factor) overlap with tools like git-quick-stats but are included so the
  report stands alone.
- **Quantitative only** — like scan-repo, this skill reports numbers and
  tables. It does not interpret trends, judge team health, or draw conclusions.
- **Bundled script** — `scripts/git-scanner.sh` runs the heavy git log parsing
  in a single pass for performance. The skill invokes it and formats the output.
- **Graceful degradation** — handles shallow clones, empty repos, and repos
  with fewer than 10 commits by producing minimal or stub reports.

## Usage

Typically run after `archeia:scan-repo` and before `archeia:write-tech-docs`.
The git report provides contributor context that enriches the architecture
docs — who owns which modules, where knowledge is concentrated, and where
collaboration patterns suggest architectural boundaries.
