---
layer: 3
depends_on: Architecture.md
required_evidence: package.json, pyproject.toml, tsconfig.json, ruff.toml, .eslintrc, Makefile, tests/
validation: all-required-sections-present, all-claims-cite-evidence, no-marketing-language, tool-names-match-configs
---

## Purpose

Standards.md defines how code is written in this repository — the tools,
conventions, and rules that make output consistent across agents and humans.
It is read by coding agents before writing or modifying code.

This document must be factual and evidence-backed. Standards are inferred
from configuration files, manifest settings, and existing code patterns. If
a standard cannot be confirmed from evidence, use:
`<!-- INSUFFICIENT EVIDENCE: [what is missing] -->`

Standards.md captures conventions that should change infrequently. Architecture
decisions (why something was chosen) belong in DECISIONS.md, not here.

---

## Required Sections

### Documentation Confidence

**Always include. Must be the first section in generated output.**

This section reports evidence quality per section, so agents and humans know
which conventions are real (configured and enforced) vs absent. Confidence
is granular — a repo can have a clear language/runtime but no linter, no
formatter, and no type checker.

Content must include:
- **Per-section confidence table:** one row per Required Section (excluding
  this one), with a confidence level and a short reason:
  - `high`: section cites a specific tool and its config file
  - `medium`: section has partial evidence (e.g., tool in manifest but no
    config file, or convention inferred from code patterns)
  - `low`: section reports "not detected" — no tool or convention found
- **Overall confidence:** derived from the per-section levels. Use the
  lowest level that applies to 2+ sections. If all sections are high, overall
  is high. If one section is low, overall is still medium (one outlier). If
  2+ sections are low, overall is low.
- **Agent guidance:** one sentence per low-confidence section telling agents
  what to do differently in that area. High-confidence sections need no
  guidance. Omit the guidance block entirely if overall is high.

**Format:**
```
| Section | Confidence | Reason |
|---------|------------|--------|
| Language and Runtime | high | Python 3.11, uv, from `pyproject.toml` and `uv.lock` |
| Formatting and Linting | low | No formatter or linter config detected |
| Typing and Static Analysis | low | No type checker config detected |
| Project Structure | high | Clear layout with standard `src/` and `tests/` |
| Naming Conventions | medium | Mostly snake_case but 12 files use camelCase |
| Testing | high | pytest configured in `pyproject.toml` |
| Error Handling and Logging | low | No structured patterns detected |

**Overall: low** (3 low, 1 medium, 3 high)

**Low-confidence guidance:**
- **Formatting and Linting:** No formatter or linter configured. Match the
  style of the nearest file. Do not introduce formatting tools without
  approval.
- **Typing and Static Analysis:** No type checker configured. Do not add
  type annotations unless the file already uses them.
- **Error Handling and Logging:** No structured patterns detected. Follow
  whatever pattern the nearest module uses.
```

For repos with no configured tooling, this section tells agents *exactly
which areas* have no conventions rather than applying a blanket "low
confidence" that makes the well-configured areas seem untrustworthy too.

### Language and Runtime

**Always include.** The language, version, runtime, and package manager.

Content must include:
- Language and version (from manifest or config)
- Runtime target (Node.js, CPython, Deno, etc.)
- Package manager (from lockfile type)
- Entry points (from manifest scripts or main field)

**Format:**
```
- **Language:** [language] [version]
- **Runtime:** [runtime]
- **Package manager:** [manager] (`[lockfile]` present)
- **Entry points:** `[path]` ([purpose])

**Evidence:** `[manifest]`, `[lockfile]`
```

### Formatting and Linting

**Always include.** The formatter, linter, and their configuration.

Infer from: config files (ruff.toml, .eslintrc*, biome.json, .prettierrc*),
manifest tool sections ([tool.ruff], [tool.black]), pre-commit config.

Content must include:
- Formatter name and config file location
- Linter name and config file location
- Auto-fix policy (if detectable from scripts or pre-commit)
- When formatting is enforced (pre-commit, CI, both, neither)

If no formatter/linter config exists, state: `No formatter/linter configuration
detected.`

**Format:**
```
- **Formatter:** [tool] (`[config file]`)
- **Linter:** [tool] (`[config file]`)
- **Auto-fix:** [yes/no, when]
- **Enforcement:** [pre-commit / CI / both / none detected]

**Evidence:** `[config files]`
```

### Typing and Static Analysis

**Always include.** The type checker and strictness level.

Infer from: tsconfig.json (strict field), mypy config, pyright config,
flow config.

Content must include:
- Type checker name
- Strictness level (from config)
- Where type checks run (CI, pre-commit, editor only)

If no type checker config exists, state: `No type checker configuration
detected.`

**Format:**
```
- **Type checker:** [tool] (`[config file]`)
- **Strictness:** [level] (from `[config field]`)
- **Enforcement:** [where it runs]

**Evidence:** `[config files]`
```

### Project Structure

**Always include.** The directory layout and module organization.

Content must include:
- Root layout (which top-level directories exist and their purpose)
- Source code location (src/, lib/, app/)
- Test location (tests/, __tests__/, spec/, test/)
- Configuration location (root configs, .config/, etc.)
- Generated/build output location (dist/, build/, .next/, etc.)

**Format:**
```
[project root]
├── [dir]/          [purpose]
├── [dir]/          [purpose]
├── [config file]   [purpose]
└── [config file]   [purpose]

**Evidence:** directory listing
```

### Naming Conventions

**Always include.** How things are named in this codebase.

Infer from: existing file names, directory names, import patterns in sampled
source files, manifest conventions.

Content must include:
- File naming pattern (kebab-case, camelCase, snake_case, PascalCase)
- Directory naming pattern
- Export/module naming pattern (if detectable from source samples)

**Format:**
```
- **Files:** [pattern] (e.g., `user-service.ts`, `user_service.py`)
- **Directories:** [pattern]
- **Exports:** [pattern] (e.g., PascalCase for classes, camelCase for functions)

**Evidence:** file listing in `[source directory]`
```

### Testing

**Always include.** The test framework, conventions, and expectations.

Infer from: test config files, test directory structure, manifest test scripts,
test file naming patterns.

Content must include:
- Test framework name
- Test file naming pattern (test_*.py, *.test.ts, *_spec.rb, etc.)
- Test directory location
- How to run tests (from manifest scripts or Makefile)

**Format:**
```
- **Framework:** [tool] (`[config file]`)
- **Test files:** `[pattern]` in `[directory]`
- **Run tests:** `[command]` (from `[manifest]` scripts)

**Evidence:** `[config file]`, `[test directory]` listing
```

### Error Handling and Logging

**Always include.** How errors are represented and logged.

Infer from: error middleware files, logging config, structured log patterns
in sampled source files, error handling utilities.

If patterns are not detectable from config or source samples, state:
`No structured error handling or logging patterns detected at Layer 3.
Conventions should be defined in DECISIONS.md.`

**Format:**
```
- **Error pattern:** [description] (e.g., custom error classes, Result types)
- **Logging:** [tool/approach] (`[config or import]`)
- **Log format:** [structured JSON / plaintext / not detected]

**Evidence:** `[source files with patterns]`
```

---

## Conditional Sections

### Dependency and Build Management

**Include if** build tooling exists (Makefile, Justfile, Taskfile, noxfile.py,
tox.ini, build scripts in manifest).

Content: build tool, lockfile strategy, dependency update policy (if detectable
from Renovate/Dependabot config).

### Pre-commit and Automation

**Include if** `.pre-commit-config.yaml` exists or manifest scripts include
lint/format/check commands.

Content: what hooks run, what scripts are available, how to set up locally.

### Deferred Work Conventions

**Always include.** How TODOs and deferred work are marked.

Infer from: existing TODO/FIXME patterns in source files (sample 2-3 files),
or use the default:

```
- Use `// TODO(name): description. Issue #N` for deferred work.
- Use the same format for `FIXME` and `HACK`.
```

---

## Inference Signals

These signals map repo evidence to Standards.md content:

| Evidence | Maps to section | Conclusion |
|----------|----------------|-----------|
| Manifest language/version field | Language and Runtime | Language, version |
| Lockfile type (uv.lock, pnpm-lock.yaml) | Language and Runtime | Package manager |
| ruff.toml, .eslintrc*, biome.json | Formatting and Linting | Linter config |
| .prettierrc*, [tool.black] | Formatting and Linting | Formatter config |
| tsconfig.json strict field | Typing and Static Analysis | TS strictness |
| mypy/pyright config | Typing and Static Analysis | Python type checking |
| Directory listing | Project Structure | Layout |
| File names in source directory | Naming Conventions | File naming pattern |
| Test config (jest, vitest, pytest) | Testing | Framework, patterns |
| Test directory structure | Testing | Test file location |
| .pre-commit-config.yaml | Pre-commit and Automation | Hook configuration |
| Makefile/Justfile targets | Dependency and Build Management | Build automation |
| Existing TODO comments in source | Deferred Work Conventions | TODO format |

---

## Quality Rubric

The self-validation pass checks these criteria:

- **COMPLETENESS:** Every Required Section is present, including Documentation
  Confidence as the first section. Language and Runtime names the language
  and package manager. Testing names the test framework. Documentation
  Confidence level is consistent with the number of "not detected" findings.
- **TRUTHFULNESS:** Tool names match what's in config files (e.g., don't say
  "uses ESLint" if only biome.json exists). All cited config files exist
  (verified by Glob). Standards are inferred from evidence, not assumed.
- **CONCISENESS:** No section exceeds 20 lines. No explanations of why a
  tool was chosen (that belongs in DECISIONS.md). No marketing language.
- **DETERMINISM:** Sections appear in the order listed above. Format blocks
  use the exact field names specified. If a tool is not detected, the section
  explicitly states "not detected" rather than omitting the field.

---

## Anti-Patterns

DO NOT produce output like this:

- `Uses industry-standard linting and formatting tools.`
  → Name the specific tools and their config files.
- `Following best practices for TypeScript development.`
  → Vague. Instead: `TypeScript with strict mode enabled. Evidence: tsconfig.json
  "strict": true`
- `Tests should cover all critical paths.`
  → Aspirational, not factual. Instead: `Test framework: vitest (vitest.config.ts).
  Test files: *.test.ts in tests/. Run: pnpm test`
- Listing tools that aren't configured in the repo (e.g., claiming the project
  uses Prettier when no .prettierrc exists).
- Inventing naming conventions not supported by actual file names in the repo.
- Recommending tools or practices not yet adopted — that belongs in DECISIONS.md.
