---
name: scan-git
version: 0.0.1
description: |
  Analyze git history to produce a team collaboration and dynamics report.
  This is the second skill in the archeia pipeline — run it after
  archeia:scan-repo, before archeia:write-tech-docs. It focuses on how
  contributors work together: integration patterns, knowledge flow,
  collaboration density, and team structure. Lightweight activity metrics
  (velocity, churn, commit patterns, bus factor) are included for context.
  Output is `.archeia/codebase/git-report.md`. Use this skill when the user wants to
  understand team dynamics, contributor patterns, or how a development team
  collaborates — not just the size or architecture of the code.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Write
---

## Purpose

Produce `.archeia/codebase/git-report.md` — a single document that answers "who builds
this and how do they work together?" in under 30 seconds of reading. Every
number must come from actual git data, not guesswork.

This skill sits between `archeia:scan-repo` and `archeia:write-tech-docs` in
the pipeline. Where scan-repo measures the codebase ("how big?") and
write-tech-docs interprets architecture ("what does it do?"), this skill
reads the git history to surface **team collaboration structure** — who
integrates code, how knowledge flows between areas, how tightly contributors
collaborate, and where rework or instability concentrates.

The core sections (Integration Patterns, Collaboration Density, Knowledge
Flow, Revert & Rework) cover ground that no standard open-source tool
addresses well. The lightweight sections (Roster, Velocity, Churn, Time
Patterns, Bus Factor) overlap with dedicated tools like git-quick-stats and
bus-factor-explorer, but are included at reduced depth so the report stands
on its own.

The boundary: this skill reports numbers and tables. It does not interpret
trends, judge team health, or draw architectural conclusions. If you find
yourself writing sentences that explain *why* a pattern exists, you've
crossed the line.

## Workflow

Run these steps in order. The whole scan should complete in under 3 minutes.

### Step 0: Preflight

Verify the environment before collecting data.

```bash
git rev-parse --is-inside-work-tree
```

If this fails, write a stub report:

```markdown
# Git Report

> Not a git repository. Run this skill from a git-initialized directory.
```

Then check the commit count and clone depth:

```bash
git rev-list --count HEAD
git rev-parse --is-shallow-repository
```

**Handling edge cases:**

- **0 commits**: write a stub report noting "Empty repository. No commits to
  analyze." and stop.
- **Fewer than 10 commits**: produce a minimal report containing only
  Contributor Roster and Integration Patterns. Add a note at the top:
  "Repository has fewer than 10 commits. Sections requiring statistical mass
  are omitted."
- **More than 50,000 commits**: limit all time-based analyses (velocity,
  churn monthly, merge trends) to the last 24 months. Add a note in the
  report header: "History limited to last 24 months (N total commits)."
- **Shallow clone**: add a warning: "Shallow clone detected. Metrics may be
  incomplete."

### Step 1: Collect Data

Run the bundled `scripts/git-scanner.sh` script to collect all git history
data in a single step. The script runs 5–6 optimized `git log` passes and
writes clean TSV files to an output directory.

```bash
# Basic usage — outputs to /tmp/archeia:scan-git-<pid>/
OUTPUT_DIR=$(bash /path/to/skills/codebase/scan-git/scripts/git-scanner.sh)

# For repos with >50k commits, limit to last 24 months:
OUTPUT_DIR=$(bash /path/to/skills/codebase/scan-git/scripts/git-scanner.sh --since 2024-04-01)

# Custom output directory:
OUTPUT_DIR=$(bash /path/to/skills/codebase/scan-git/scripts/git-scanner.sh --output-dir /tmp/my-scan)
```

The script produces these TSV files (tab-delimited, no headers):

| File                  | Fields                                              | Feeds sections                             |
|-----------------------|-----------------------------------------------------|--------------------------------------------|
| `preflight.tsv`       | key, value                                          | Step 0 edge case handling                  |
| `aliases.tsv`         | email, canonical_name                               | Author deduplication (all sections)        |
| `roster.tsv`          | author, commits, added, deleted, first_date, last_date | Contributor Roster                        |
| `monthly.tsv`         | month, author, commits, added, deleted              | Velocity, Code Churn monthly               |
| `yearly.tsv`          | year, author, commits, added, deleted               | Velocity (yearly table)                    |
| `file_churn.tsv`      | file, added, deleted, commit_count                  | Code Churn, Rework Files                   |
| `file_authors.tsv`    | file, directory, author (deduplicated)              | Knowledge Spread, Cross-pollination        |
| `dir_authors.tsv`     | directory, author, commit_count                     | Knowledge Flow, Bus Factor                 |
| `merges.tsv`          | hash, author, committer, date, subject              | Integration Patterns                       |
| `coauthors.tsv`       | commit_author, coauthor_name, hash                  | Collaboration Density                      |
| `time_patterns.tsv`   | day_of_week, hour                                   | Commit Time Patterns                       |
| `subjects.tsv`        | hash, date, subject                                 | Revert detection, Commit Patterns          |
| `cross_dir_commits.tsv` | count (single value)                              | Collaboration Ratio                        |
| `reverts.tsv`         | date, month, subject                                | Revert & Rework                            |
| `fix_after_fix.tsv`   | file, occurrences (only if conventional commits)    | Fix-after-Fix                              |

**Author aliasing:** The script unifies contributors who use multiple git
configs (different name/email combos) by using email as the dedup key. The
most recent name associated with each email becomes the canonical display
name. All author fields in all TSVs already contain resolved canonical
names. Check `aliases.tsv` to see the email-to-name mapping.

Read these TSV files to build each report section. The parsing is already
done — you just need to sort, aggregate, and format the data into markdown
tables.

**Check `preflight.tsv` first** for edge cases (not_a_repo, commit_count,
is_shallow, has_conventional). Handle these before proceeding to report
sections.

---

### Core Sections

These sections are the unique value of this skill — no standard open-source
tool covers them well.

### Step 2: Integration Patterns

Who merges code, how often, and what does the merge topology look like. This
reveals the team's code integration workflow and identifies key integrators.

From `merges.tsv` and `roster.tsv`, extract:

- **Merge count** (lines in `merges.tsv`) and **non-merge count** (sum of commits in `roster.tsv`)
- **Merge frequency**: merges per 100 commits
- **Avg commits per merge**: non-merge commits / merge count (proxy for
  branch/PR size)
- **Integrator table**: each merge-commit author, their merge count, and
  their % of total merges. Top 10 only, sorted by count descending.
- **Integration style**: classify each merge subject (5th field in `merges.tsv`):
  - Contains `#[0-9]+` → PR-referenced
  - Contains `Merge branch` or `Merge pull request` → branch-named
  - Other → unclassified
  Report the % breakdown of each style.
- **Review signal**: count lines in `merges.tsv` where author (field 2) ≠
  committer (field 3). This is a proxy for "someone else merged your code."
- **Merges per month**: last 12 months (or full history if shorter)

If no merge commits exist, report:

```
Linear history detected (rebase or squash workflow). No merge commits to analyze.
```

And skip the integrator table and merge trend.

**Format:**

```markdown
## Integration Patterns

- Merge commits: 342
- Non-merge commits: 1,847
- Merge frequency: 16 per 100 commits
- Avg commits per merge: 5.4

### Integrators

| Integrator    | Merges | % of Total |
|---------------|--------|------------|
| alice         | 198    | 57.9%      |
| bob           | 112    | 32.7%      |
| carol         | 32     | 9.4%       |

### Integration Style

| Style            | Count | %    |
|------------------|-------|------|
| PR-referenced    | 287   | 83.9% |
| Branch-named     | 43    | 12.6% |
| Unclassified     | 12    | 3.5%  |

- Review signal: 298 merges (87.1%) where author ≠ committer

### Merges per Month

| Month   | Merges |
|---------|--------|
| 2025-05 | 28     |
| 2025-04 | 31     |
| ...     | ...    |
```

### Step 3: Collaboration Density

How much do contributors work together vs in isolation. This surfaces
pair-programming patterns, shared ownership, and cross-cutting work.

From `coauthors.tsv`, `file_authors.tsv`, `dir_authors.tsv`, and
`cross_dir_commits.tsv`, extract:

- **Co-authored commits**: count unique hashes in `coauthors.tsv`. Report
  count and % of total non-merge commits. If `coauthors.tsv` is empty,
  report "No co-authored commits found." and skip the Co-author Pairs
  table entirely — do not show an empty table or a "— | 0" row.
- **Co-author pairs**: from `coauthors.tsv`, group by (commit_author,
  coauthor_name), normalize pair order (alphabetical), count occurrences.
  List the top 10 most frequent pairs. Only show this table if there are
  co-authored commits.
- **Cross-pollination**: from `dir_authors.tsv`, count unique authors per
  directory. **Filter to directories with ≥10 total commits** to avoid
  cluttering the table with trivial dot-directories. Produce a table
  sorted by contributor count descending.
- **Collaboration ratio**: read `cross_dir_commits.tsv` (single count).
  Report as count and % of total non-merge commits.
- **Review signals**: already captured in Step 2; reference the number here
  for context.

**Format:**

```markdown
## Collaboration Density

- Co-authored commits: 47 (2.5% of non-merge commits)
- Cross-directory commits: 312 (16.9%)

### Co-author Pairs

| Pair              | Co-authored Commits |
|-------------------|---------------------|
| alice + bob       | 18                  |
| carol + dave      | 12                  |
| alice + carol     | 9                   |
| ...               | ...                 |

### Cross-pollination

| Directory   | Contributors |
|-------------|-------------|
| src/        | 6           |
| tests/      | 5           |
| packages/   | 3           |
| docs/       | 2           |
| config/     | 1           |
```

### Step 4: Knowledge Flow

Where expertise concentrates and how it moves between contributors and
areas. This identifies knowledge islands, succession risks, and the breadth
of each contributor's involvement.

From `dir_authors.tsv`, `file_churn.tsv`, and `file_authors.tsv`, extract:

- **Per-directory contributor table**: from `dir_authors.tsv`, for each
  directory list unique contributor count, the top contributor (by commit
  count), their % of that directory's commits, and the 2nd contributor's %.
  **Filter to directories with ≥10 total commits.** Directories below this
  threshold are noise (config dirs, one-off scripts).
- **Single-author directories**: directories in `dir_authors.tsv` (with
  ≥10 commits) where only one author appears.
- **Knowledge spread**: take the top 20 files from `file_churn.tsv` (by
  commit_count), then count unique authors per file from `file_authors.tsv`.
  Files with only 1 contributor are knowledge islands.
- **Contributor reach**: from `dir_authors.tsv`, count unique directories
  per author. Report as a table sorted by directory count descending.
- **Succession signal**: for each directory (with ≥10 commits) where the
  historically dominant contributor (highest commit %) has been inactive
  for >90 days, check whether another active contributor has committed
  there in the last 90 days. Report directories where succession has
  occurred vs where no active contributor remains. Skip directories below
  the commit threshold.

**Format:**

```markdown
## Knowledge Flow

### Directory Ownership

| Directory   | Contributors | Top Contributor | Top % | 2nd %  |
|-------------|-------------|-----------------|-------|--------|
| src/        | 6           | alice           | 42%   | 28%    |
| tests/      | 5           | bob             | 55%   | 20%    |
| packages/   | 3           | alice           | 67%   | 22%    |
| docs/       | 2           | carol           | 80%   | 20%    |
| config/     | 1           | alice           | 100%  | —      |

- Single-author directories: 1 of 5

### Knowledge Spread (top 20 files)

| File                     | Changes | Contributors |
|--------------------------|---------|-------------|
| src/lib/api.ts           | 87      | 4           |
| src/components/Header.ts | 64      | 1           |
| ...                      | ...     | ...         |

- Knowledge islands (1 contributor): 6 of 20

### Contributor Reach

| Contributor | Directories Touched |
|-------------|---------------------|
| alice       | 5                   |
| bob         | 3                   |
| carol       | 2                   |
| dave        | 1                   |

### Succession

| Directory | Dominant (inactive) | Active Successor | Status      |
|-----------|---------------------|------------------|-------------|
| config/   | eve                 | alice            | Covered     |
| docs/     | frank               | —                | Uncovered   |
```

### Step 5: Revert & Rework

Signals of instability, integration friction, or rework. These are not
judgments — a high revert ratio might reflect a healthy "revert first, fix
later" culture or it might reflect integration problems. The report provides
the numbers; interpretation belongs elsewhere.

From `reverts.tsv`, `file_churn.tsv`, and `fix_after_fix.tsv`, extract:

- **Revert count**: line count of `reverts.tsv`.
- **Revert ratio**: reverts per 1,000 commits.
- **Revert clusters**: group `reverts.tsv` by month (field 2). If >50% of
  reverts concentrate in a single month, flag that month.
- **Rework files**: from `file_churn.tsv`, identify the top 10 files with
  the highest churn ratio (deleted / added), filtered to files with at
  least 100 total line changes (added + deleted). These are files where
  code is written and substantially rewritten.
- **Fix-after-fix** (only if `has_conventional` is `true` in
  `preflight.tsv`): read `fix_after_fix.tsv` for files and occurrence
  counts. Report total count and list the top 5 files. Skip this metric
  entirely if the repo doesn't use conventional commits.

**Format:**

```markdown
## Revert & Rework

- Reverts: 14 (6.4 per 1,000 commits)
- Revert cluster: 2025-02 (8 of 14 reverts, 57%)

### Rework Files

| File                     | Added  | Deleted | Churn Ratio |
|--------------------------|--------|---------|-------------|
| src/lib/api.ts           | 1,240  | 890     | 0.72        |
| src/models/user.ts       | 620    | 445     | 0.72        |
| ...                      | ...    | ...     | ...         |

### Fix-after-Fix

- Repeated fixes within 7 days: 8 occurrences across 4 files

| File                  | Occurrences |
|-----------------------|-------------|
| src/lib/payments.ts   | 3           |
| src/auth/session.ts   | 2           |
| ...                   | ...         |
```

---

### Lightweight Sections

These overlap with dedicated tools (git-quick-stats, bus-factor-explorer,
etc.) but are included at reduced depth so the report is self-contained.

### Step 6: Contributor Roster

The foundation table that other sections reference. Read `roster.tsv` —
each row has: author, commits, added, deleted, first_date, last_date.

- **Status**: "active" if last_date is within 90 days of the scan date,
  "inactive" otherwise. Detect the platform for date math: `date -v-90d` on
  macOS, `date -d '90 days ago'` on Linux.
- **Bots**: mark accounts whose name contains `[bot]`, `dependabot`,
  `renovate`, or `github-actions` with a `(bot)` suffix.
- Sort by commit count descending.

**Format:**

```markdown
## Contributor Roster

6 contributors (4 active, 2 inactive, 0 bots)

| Contributor | Commits | Lines +  | Lines -  | First      | Last       | Status   |
|-------------|---------|----------|----------|------------|------------|----------|
| alice       | 423     | 18,420   | 7,230    | 2024-01-15 | 2025-05-18 | active   |
| bob         | 312     | 12,100   | 5,670    | 2024-02-03 | 2025-05-20 | active   |
| carol       | 187     | 8,900    | 3,440    | 2024-03-10 | 2025-04-28 | active   |
| dave        | 98      | 4,200    | 1,890    | 2024-06-01 | 2025-05-15 | active   |
| eve         | 45      | 2,100    | 980      | 2024-01-20 | 2024-09-14 | inactive |
| frank       | 12      | 540      | 210      | 2024-04-05 | 2024-07-22 | inactive |
```

### Step 7: Velocity Summary

Lightweight monthly activity overview. From `monthly.tsv`, group by month
(field 1) and count unique authors per month.

- Show last 12 **complete** months, or full history if shorter. **Exclude
  the current (incomplete) month** — it always looks artificially low and
  distorts the trend calculation.
- Summary stats: average commits/month, average active contributors/month
  (computed over complete months only).
- **Trend**: compare the average commits/month over the last 3 complete
  months to the prior 3 complete months. Report as a % change ("+15%" or
  "-22%"). If fewer than 6 complete months of history, report "N/A
  (insufficient history)".

Also produce a **yearly velocity table** from `yearly.tsv`:

| Year | Commits | Active Contributors | Commits/Contributor |

Show all years in the repo's history. This gives a longer-horizon view
that monthly data can't.

**Format:**

```markdown
## Velocity

Avg 91 commits/month | Avg 4.2 active contributors/month | Trend: +12%

### Monthly (last 12 complete months)

| Month   | Commits | Active Contributors | Commits/Contributor |
|---------|---------|---------------------|---------------------|
| 2025-05 | 104     | 4                   | 26.0                |
| 2025-04 | 98      | 5                   | 19.6                |
| 2025-03 | 87      | 4                   | 21.8                |
| ...     | ...     | ...                 | ...                 |

### Yearly

| Year | Commits | Active Contributors | Commits/Contributor |
|------|---------|---------------------|---------------------|
| 2025 | 1,143   | 6                   | 190.5               |
| 2024 | 987     | 5                   | 197.4               |
| 2023 | 1,245   | 8                   | 155.6               |
| ...  | ...     | ...                 | ...                 |
```

### Step 8: Code Churn Highlights

Focused on what's useful, not exhaustive. From `file_churn.tsv` and
`monthly.tsv`:

- **Top 15 most-churned files**: sorted by total line changes (added +
  deleted) across all time. Filter binary files (lines showing `-` in
  numstat).
- **Top 15 most-frequently-changed files**: sorted by commit count touching
  each file.
- **Monthly net lines**: for the last 12 months, show added - deleted as a
  compact single-row summary.
- **Overall churn ratio**: total deleted / total added across the repo.

Renamed files will appear as separate entries because `git log` without
`--follow` treats them as distinct paths. Note this limitation in the
section header.

**Format:**

```markdown
## Code Churn

Overall churn ratio: 0.58 (total deleted / total added)

Note: renamed files appear as separate entries (git limitation without --follow).

### Most Churned (by total line changes)

| File                     | Added  | Deleted | Total  |
|--------------------------|--------|---------|--------|
| src/lib/api.ts           | 1,240  | 890     | 2,130  |
| ...                      | ...    | ...     | ...    |

### Most Frequently Changed (by commit count)

| File                     | Commits |
|--------------------------|---------|
| src/lib/api.ts           | 87      |
| ...                      | ...     |

### Monthly Net (last 12 months)

| 05 | 04 | 03 | 02 | 01 | 12 | 11 | 10 | 09 | 08 | 07 | 06 |
|----|----|----|----|----|----|----|----|----|----|----|----|
| +1.2k | +890 | +2.1k | -340 | +1.5k | +780 | +950 | +1.1k | +640 | +2.3k | +1.8k | +920 |
```

### Step 9: Commit Time Patterns

Quick temporal snapshot. From `time_patterns.tsv`:

- **Day of week**: table with commit counts and % of total for each day.
  Highlight the peak day.
- **Hour of day (UTC)**: table with commit counts and a simple bar using `█`
  characters, scaled so the peak hour gets 10 blocks. Highlight the peak
  hour.

From `subjects.tsv` (field 3 is the subject line):
- **Average commit message subject length** (in characters).
- **Conventional commit prefixes**: check `has_conventional` in
  `preflight.tsv`. If true, scan subjects for prefixes and show a breakdown
  table with prefix and count. Otherwise, note "No conventional commit
  convention detected."

**Format:**

```markdown
## Commit Patterns

### Day of Week

| Day       | Commits | %     |
|-----------|---------|-------|
| Tuesday   | 412     | 22.3% | ← peak
| Wednesday | 389     | 21.1% |
| Thursday  | 356     | 19.3% |
| Monday    | 341     | 18.5% |
| Friday    | 287     | 15.5% |
| Saturday  | 34      | 1.8%  |
| Sunday    | 28      | 1.5%  |

### Hour of Day (UTC)

| Hour | Commits | Distribution       |
|------|---------|--------------------|
| 09   | 187     | ████████           |
| 10   | 234     | ██████████         | ← peak
| 11   | 210     | █████████          |
| ...  | ...     | ...                |

- Avg message length: 48 chars

### Commit Prefixes

| Prefix   | Count |
|----------|-------|
| feat     | 342   |
| fix      | 287   |
| chore    | 156   |
| docs     | 45    |
| refactor | 38    |
| test     | 22    |
```

### Step 10: Bus Factor Summary

Simplified directory-level view. From `dir_authors.tsv` and `roster.tsv`:

- **Per top-level directory**: unique contributor count, top contributor, top
  contributor's % of commits in that directory. **Filter to directories
  with ≥10 total commits** (same threshold as Knowledge Flow).
- **Flagged directories**: where top contributor holds >75% of commits.
  This is a mechanical threshold, not a judgment — a directory can have
  many contributors but still be dominated by one person (e.g., 90%
  concentration with 7 contributors is still a bus factor risk).
- **Summary**: N flagged directories out of M total.
- **Repo-wide bus factor estimate**: simulate removing the top contributor
  (by overall commit count). Count how many directories lose their only
  active contributor. Report as: "Removing [name] would leave N of M
  directories with no active contributor."

Note: this is a simplified view. For deep bus factor modeling with treemap
visualization and turnover simulation, use
[bus-factor-explorer](https://github.com/JetBrains-Research/bus-factor-explorer)
or [SOM-Research/busfactor](https://github.com/SOM-Research/busfactor).

**Format:**

```markdown
## Bus Factor

3 of 5 directories flagged (top contributor >75%)

| Directory   | Contributors | Top Contributor | Top % | Flagged |
|-------------|-------------|-----------------|-------|---------|
| src/        | 6           | alice           | 42%   |         |
| tests/      | 5           | bob             | 55%   |         |
| packages/   | 3           | alice           | 67%   |         |
| docs/       | 7           | carol           | 80%   | ⚠       |
| config/     | 1           | alice           | 100%  | ⚠       |
| frontend/   | 7           | alice           | 90%   | ⚠       |

Removing alice would leave 1 of 5 directories with no active contributor.
```

---

### Step 11: Write the Report

Create `.archeia/codebase/git-report.md`. Assemble all sections in this order:

```markdown
# Git Report

> {N} contributors ({N} active) | {N} commits | {workflow} | {N} commits/month avg
```

The summary line identifies the team at a glance:
- **Contributors**: total with active count in parens
- **Commits**: total commit count (merges + non-merges)
- **Workflow**: "merge" if >5% of commits are merges, "linear" if ≤5%, "mixed" if between 5–15%
- **Commits/month avg**: average over the full history

Section order:

1. Integration Patterns
2. Collaboration Density
3. Knowledge Flow
4. Revert & Rework
5. Contributor Roster
6. Velocity
7. Code Churn
8. Commit Patterns
9. Bus Factor

Core sections come first because they contain the unique analysis.
Lightweight sections follow as supporting context.

## What NOT to Include

This skill reads git history for team dynamics. It does not:

- Duplicate scan-repo's Git Vitals (repo age, total commits, contributor
  count, last commit, branches) — those belong in ScanReport.md
- Perform blame-based line ownership analysis — use
  [git-fame](https://github.com/casperdcl/git-fame)
- Generate code age or survival curves — use
  [git-of-theseus](https://github.com/erikbern/git-of-theseus)
- Produce burndown charts — use
  [hercules](https://github.com/src-d/hercules)
- Measure repo object/pack health — use
  [git-sizer](https://github.com/github/git-sizer)
- Map per-file responsibility matrices — use
  [gitinspector](https://github.com/ejwa/gitinspector)
- Provide deep velocity analytics with visualizations — use
  [git-quick-stats](https://github.com/git-quick-stats/git-quick-stats) or
  [CNCF Velocity](https://github.com/cncf/velocity)
- Model bus factor with turnover simulation — use
  [bus-factor-explorer](https://github.com/JetBrains-Research/bus-factor-explorer)
  or [SOM-Research/busfactor](https://github.com/SOM-Research/busfactor)
- Enforce conventional commit conventions — use
  [cocogitto](https://github.com/cocogitto/cocogitto) or
  [convco](https://convco.github.io/)
- Make qualitative judgments about team health, productivity, or code quality
- Interpret trends or draw conclusions ("the team is slowing down")
- Describe architecture, design patterns, or system topology
- Require any tool installation beyond git and standard Unix utilities

If you find yourself writing sentences that explain *why* a pattern exists
or *how* the team should change, you've crossed the line. Stick to counts,
lists, and tables.

## Expected Output

- `.archeia/codebase/git-report.md`
