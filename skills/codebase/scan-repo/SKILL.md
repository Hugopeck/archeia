---
name: scan-repo
version: 0.0.1
description: |
  Scan a repository and produce a quantitative metrics report. This is the
  entry-point skill for the archeia documentation pipeline — run it first,
  before archeia:write-tech-docs. It measures LOC, token estimates, file
  counts, module structure, README coverage, dependency counts, test
  footprint, and git vitals. Output is `.archeia/codebase/scan-report.md`. Use this
  skill whenever the user wants a quick repo snapshot, size estimate, or
  needs to understand the scale of a codebase before deeper analysis.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Write
---

## Purpose

Produce `.archeia/codebase/scan-report.md` — a single scannable document that answers
"how big is this repo, what's in it, and where are the gaps?" in under 30
seconds of reading. Every number in the report must come from actual
measurement, not guesswork.

This skill deliberately avoids architectural interpretation. It counts and
measures; the downstream `archeia:write-tech-docs` skill interprets and
narrates. The boundary: scan-repo answers **"how much?"** and **"how many?"**;
write-tech-docs answers **"what does it do?"** and **"how does it work?"**.

## Workflow

Run these steps in order. The whole scan should complete in under 2 minutes.

### Step 1: Measure Size

Count lines of code by language. Use `find` + `wc` or a tool like `tokei`/
`cloc` if available on the system. Fall back to manual counting with `wc -l`
grouped by file extension if no counting tool is installed.

Produce a table:

| Language | Files | Lines |
|----------|-------|-------|

Sort by lines descending. Group minor languages (<1% of total) into "Other".
Every row must have a numeric Lines value — never use a dash or blank.

### Step 2: Estimate Tokens

Estimate the token count for the entire repo's text content (excluding
binary files, node_modules, .git, vendored deps, lockfiles, and build
artifacts). Use a simple heuristic: **bytes / 4** for an approximate token
count. This is a planning estimate, not a precise measurement.

Break down by top-level directory:

| Directory | Est. Tokens | % of Total |
|-----------|-------------|------------|

### Step 3: Map Structure

Generate a directory tree to depth 2, annotated with file counts per
directory. Use `find` to count files in each directory. Example format:

```
repo-root/                    (142 files)
├── src/                      (87 files)
│   ├── components/           (34 files)
│   ├── lib/                  (12 files)
│   └── pages/                (8 files)
├── tests/                    (23 files)
└── docs/                     (5 files)
```

### Step 4: Identify Modules

Detect subsystems, packages, or workspace members. Look for:
- `workspaces` field in package.json
- `packages/` or `apps/` directories (monorepo signals)
- Top-level directories under `src/` or `lib/` with their own manifests
- Cargo workspace members, Go modules, Python packages with `__init__.py`

List each module with its source file count.

### Step 5: Audit README Coverage

Find every directory that contains 5 or more non-generated files (counting
recursively). "Non-generated" means: not inside `node_modules/`, `.git/`,
`__pycache__/`, `dist/`, `build/`, or migration directories; and not
lockfiles or build artifacts. Count files of **any** extension the repo
actually uses — not just traditional code languages. A skill repo full of
`.md` and `.sh` files still needs READMEs; a config-heavy directory full of
`.yml` files does too.

Apply the threshold consistently: use the same file-counting logic for
every directory in the repo. Do not go deeper than 2 levels below module
roots to avoid inflating the table with trivial subdirectories.

Produce a table:

| Directory | Source Files | Has README |
|-----------|-------------|------------|

End with a count: **X of Y directories need READMEs**.

### Step 6: Count Dependencies

For each manifest file found (package.json, pyproject.toml, Cargo.toml,
go.mod, Gemfile, composer.json, pom.xml, build.gradle):

| Manifest | Direct Deps | Dev Deps |
|----------|-------------|----------|

### Step 7: Measure Test Footprint

Count test files by looking for common patterns:
- Files matching `*test*`, `*spec*`, `*_test.*`, `test_*.*`
- Files inside `tests/`, `test/`, `__tests__/`, `spec/` directories

Report:
- Test file count
- Source file count (non-test, non-config, non-doc)
- Test coverage: **X%** (test files / source files * 100, rounded to nearest integer)

Detect which test frameworks are configured (look at manifest devDeps,
config files like jest.config.*, vitest.config.*, pytest.ini, etc.).

### Step 8: Git Vitals

If the directory is a git repo, collect:
- **Repo age**: date of first commit
- **Total commits**: `git rev-list --count HEAD`
- **Contributors**: `git shortlog -sn --no-merges HEAD | wc -l`
- **Last commit**: date of most recent commit
- **Branch count**: `git branch -r | wc -l` (remote branches)

### Step 9: Collect Signals

Gather quick counts for:
- **CI workflows**: count files in `.github/workflows/`, `.gitlab-ci.yml`,
  `.circleci/`
- **Docker**: note presence of Dockerfile, docker-compose.yml; count
  services in docker-compose if present
- **TODO/FIXME density**: `grep -r "TODO\|FIXME"` count, broken down by
  top-level directory
- **Entry points**: count files named `main.*`, `index.*`, `app.*`,
  `server.*` in source directories
- **Large files**: list files over 1MB (excluding .git, node_modules)

### Step 10: Audit Tooling Gaps

Check for the presence of standard development tooling. For each signal,
report whether the file or config exists — nothing more. Do not interpret
or recommend.

| Signal | What to look for | Status |
|--------|-----------------|--------|
| Linter config | `.eslintrc*`, `biome.json`, `ruff.toml`, `[tool.ruff]` in `pyproject.toml`, `clippy.toml` | Found / Not found |
| Formatter config | `.prettierrc*`, `biome.json`, `[tool.black]` in `pyproject.toml`, `rustfmt.toml` | Found / Not found |
| Type checker config | `tsconfig.json`, `[tool.mypy]` in `pyproject.toml`, `pyrightconfig.json` | Found / Not found |
| Test framework config | `jest.config.*`, `vitest.config.*`, `pytest.ini`, `[tool.pytest]`, `phpunit.xml` | Found / Not found |
| CI/CD workflows | `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/` | Found / Not found |
| Lockfile | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `uv.lock`, `poetry.lock`, `Cargo.lock`, `go.sum` | Found / Not found |
| Containerization | `Dockerfile`, `docker-compose.yml` | Found / Not found |
| Pre-commit hooks | `.pre-commit-config.yaml`, `.husky/` | Found / Not found |

End with a count: **X of 8 standard tooling signals detected.**

Also check naming consistency in source files. Count files in the primary
source directory grouped by naming pattern:

| Pattern | Files | Example |
|---------|-------|---------|
| snake_case | N | `user_service.py` |
| camelCase | N | `userService.ts` |
| kebab-case | N | `user-service.ts` |
| PascalCase | N | `UserService.ts` |

Only include patterns with at least 1 file. If all files follow one pattern,
note: **Consistent: [pattern]**. If multiple patterns appear, note:
**Mixed: [N] patterns detected.** This is a count, not a judgment.

### Step 11: Write the Report

Create `.archeia/codebase/scan-report.md` with the following structure. Use only the
data collected above — no interpretation, no architectural conclusions.

```markdown
# Scan Report

> {Language} / {Framework} / {PackageManager} | {LOC}k LOC | {N} modules | ~{Tokens}k tokens

The summary line identifies the repo at a glance. For each slot:
- **Language**: the dominant language by LOC (e.g., "Python", "TypeScript")
- **Framework**: the primary *application* framework from manifest deps
  (e.g., "Django", "Next.js", "Rails", "FastAPI"). Do NOT put test
  frameworks (pytest, jest), linters, or build tools here. If no
  application framework is detected, use "—"
- **PackageManager**: the tool used to install deps (pip, uv, pnpm, cargo, etc.).
  If none detected, use "—"

## Size

{LOC table from Step 1}

## Token Estimates

{Token table from Step 2}

## Structure

{Tree from Step 3}

## Modules

{Module list from Step 4, or "Single-package repository" if none found}

## README Coverage

{Table from Step 5}
{Count of directories needing READMEs}

## Dependencies

{Table from Step 6}

## Test Footprint

{Metrics from Step 7}

## Git Vitals

{Stats from Step 8, or "Not a git repository" if not applicable}

## Signals

{Counts from Step 9, as a compact list}

## Tooling Gaps

{Table from Step 10}
{Count of signals detected}
{Naming consistency table and summary from Step 10}
```

## Example Output

This is a truncated example showing the tone, density, and formatting to
aim for. Every section follows this pattern — numbers and tables, no prose.

```markdown
# Scan Report

> TypeScript / Next.js / pnpm | 45k LOC | 3 packages | ~180k tokens

## Size

| Language   | Files | Lines  |
|------------|-------|--------|
| TypeScript | 312   | 38,420 |
| CSS        | 45    | 4,210  |
| JSON       | 28    | 1,890  |
| Other      | 14    | 480    |
| **Total**  | **399** | **45,000** |

## Token Estimates

| Directory    | Est. Tokens | % of Total |
|--------------|-------------|------------|
| src/         | 112,000     | 62%        |
| packages/ui/ | 38,000      | 21%        |
| tests/       | 19,000      | 11%        |
| config/      | 6,400       | 4%         |
| docs/        | 4,600       | 2%         |

## Structure

repo-root/                        (399 files)
├── src/                          (187 files)
│   ├── app/                      (42 files)
│   ├── components/               (89 files)
│   └── lib/                      (56 files)
├── packages/                     (134 files)
│   ├── ui/                       (98 files)
│   └── shared/                   (36 files)
├── tests/                        (51 files)
└── docs/                         (8 files)

## Modules

| Module          | Source Files |
|-----------------|-------------|
| src (main app)  | 187         |
| packages/ui     | 98          |
| packages/shared | 36          |

## README Coverage

| Directory          | Source Files | Has README |
|--------------------|-------------|------------|
| src/               | 187         | Yes        |
| src/components/    | 89          | No         |
| src/lib/           | 56          | No         |
| packages/ui/       | 98          | Yes        |
| packages/shared/   | 36          | No         |

**3 of 5 directories need READMEs**

## Dependencies

| Manifest              | Direct Deps | Dev Deps |
|-----------------------|-------------|----------|
| package.json (root)   | 4           | 12       |
| packages/ui           | 8           | 3        |
| packages/shared       | 2           | 1        |

## Test Footprint

- Test files: 51
- Source files: 321
- Test coverage: 16%
- Frameworks: vitest (vitest.config.ts)

## Git Vitals

- Repo age: 2024-01-15 (first commit)
- Total commits: 847
- Contributors: 6
- Last commit: 2025-05-20
- Remote branches: 12

## Signals

- CI workflows: 3 (.github/workflows/)
- Docker: Dockerfile present, docker-compose.yml with 3 services
- TODO/FIXME: 24 total (src/ 18, packages/ 4, tests/ 2)
- Entry points: 2 (src/app/main.ts, packages/ui/index.ts)
- Large files (>1MB): 1 (public/logo.png, 2.3MB)

## Tooling Gaps

| Signal | Status |
|--------|--------|
| Linter config | Found (biome.json) |
| Formatter config | Found (biome.json) |
| Type checker config | Found (tsconfig.json) |
| Test framework config | Found (vitest.config.ts) |
| CI/CD workflows | Found (.github/workflows/) |
| Lockfile | Found (pnpm-lock.yaml) |
| Containerization | Found (Dockerfile, docker-compose.yml) |
| Pre-commit hooks | Not found |

**7 of 8 standard tooling signals detected.**

| Pattern | Files | Example |
|---------|-------|---------|
| kebab-case | 287 | `user-service.ts` |
| PascalCase | 25 | `UserProvider.tsx` |

**Mixed: 2 patterns detected.**
```

### What NOT to Include

This skill must stay on the quantitative side of the boundary with
`archeia:write-tech-docs`. Do not:

- Describe what modules or components *do* (that's Architecture.md)
- Map dependencies to architectural roles (that's the inference signal table)
- Narrate data flow or system topology (that's C4 diagrams)
- Prescribe coding standards or conventions (that's Standards.md)
- Write setup instructions or dev commands (that's Guide.md)
- Make qualitative judgments about code quality

If you find yourself writing sentences that explain *why* something exists
or *how* it works, you've crossed the line. Stick to counts, lists, and
tables.

## Expected Output

- `.archeia/codebase/scan-report.md`
