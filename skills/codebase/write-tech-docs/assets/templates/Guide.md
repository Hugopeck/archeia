---
layer: 3
depends_on: Architecture.md, Standards.md
required_evidence: package.json, pyproject.toml, Makefile, Dockerfile, .github/workflows/, README.md
validation: all-required-sections-present, all-commands-from-evidence, no-invented-workflows, all-cited-paths-exist
---

## Purpose

Guide.md is the operational handbook for the repository. It tells a developer
(or coding agent) how to set up, run, test, and deploy the project. Every
command and workflow must come from actual manifest scripts, Makefiles, CI
configs, or README instructions — not from general knowledge about the
framework.

This document must be factual and evidence-backed. Every command must
reference where it was found. If a workflow cannot be determined from
evidence, use:
`<!-- INSUFFICIENT EVIDENCE: [what is missing] -->`

Guide.md answers "how do I do X?" while Standards.md answers "what rules
apply when I do X?" and Architecture.md answers "what is X and where does
it live?"

---

## Required Sections

### Prerequisites

**Always include.** What must be installed before working on this project.

Infer from: manifest engine fields, .tool-versions, .nvmrc, .python-version,
Dockerfile base image, README setup instructions.

Content must include:
- Language runtime and version
- Package manager
- System dependencies (databases, services from docker-compose)
- Any version manager (nvm, pyenv, asdf, mise, rtx)

**Format:**
```
- [Runtime] [version] (from `[evidence file]`)
- [Package manager] (from `[lockfile]`)
- [System dependency] (from `[docker-compose.yml]` or `[README.md]`)

**Evidence:** `[files]`
```

### Setup

**Always include.** Step-by-step instructions to go from a fresh clone to a
working dev environment.

Infer from: README.md setup/install section, manifest scripts (install,
setup, prepare), Makefile targets (setup, install, init), docker-compose
configuration.

Content must be numbered steps with exact commands:

```
1. Clone and install dependencies:
   `[install command]` (from `[manifest]` or `[README]`)

2. Set up environment:
   `cp .env.example .env` (if `.env.example` exists)

3. Start services:
   `[docker-compose or service start command]` (if applicable)

4. Initialize database:
   `[migration command]` (if detectable)

**Evidence:** `[files]`
```

If setup steps cannot be fully determined, list what is known and mark
gaps with `<!-- INSUFFICIENT EVIDENCE -->`.

### Local Development

**Always include.** How to run the project locally for development.

Infer from: manifest scripts (dev, start, serve, watch), Makefile targets
(dev, run, serve), Procfile, README development section.

Content must include:
- Dev server command
- Watch/hot-reload behavior (if detectable)
- How to access the running application (port, URL)

**Format:**
```
Run the dev server:
`[dev command]` (from `[manifest]` scripts.[script name])

[Access at http://localhost:[port] if detectable from config]

**Evidence:** `[files]`
```

### Testing

**Always include.** How to run tests.

Infer from: manifest test scripts, test config files, Makefile test targets,
CI workflow test steps.

Content must include:
- Run all tests command
- Run single test file (if convention is detectable)
- Test coverage command (if configured)
- CI test configuration (if different from local)

**Format:**
```
Run all tests:
`[test command]` (from `[manifest]` scripts.test)

Run a specific test:
`[single test command]` (if detectable)

Coverage:
`[coverage command]` (if configured)

**Evidence:** `[files]`
```

### Common Tasks

**Always include.** Frequently needed commands extracted from manifest scripts,
Makefile targets, or README sections.

Present as a table:

| Task | Command | Source |
|------|---------|--------|
| [task] | `[command]` | `[manifest]` scripts.[name] |
| [task] | `[command]` | `Makefile` target [name] |

Include all commands found in manifest scripts, Makefile targets, or
Justfile recipes. Exclude internal/private scripts (those starting with
underscore or prefixed with pre/post hooks).

---

## Conditional Sections

### Lint and Format

**Include if** lint/format commands exist in manifest scripts or Makefile.

Content: exact commands for running linter, formatter, and auto-fix.

### Database

**Include if** database-related config or migration tools are detected
(Alembic, Prisma, Drizzle, ActiveRecord, Diesel, Ecto, Knex).

Content: migration commands, seed commands, database reset workflow.

### Release and Deployment

**Include if** deployment config or release scripts exist.

Content: deploy command, release workflow, environment management.
Reference CI/CD workflow files for automated deploy steps.

### Docker

**Include if** Dockerfile or docker-compose.yml exists.

Content: build command, run command, compose up/down, useful compose
commands.

### Debugging

**Include if** debugging config exists (launch.json, debug scripts in
manifest, debugger dependencies).

Content: how to attach a debugger, useful debug commands, log locations.

---

## Inference Signals

These signals map repo evidence to Guide.md content:

| Evidence | Maps to section | Conclusion |
|----------|----------------|-----------|
| .nvmrc, .python-version, .tool-versions | Prerequisites | Runtime version |
| Manifest engine field | Prerequisites | Required runtime version |
| Manifest scripts.install/setup | Setup | Install commands |
| .env.example | Setup | Environment setup step |
| docker-compose.yml | Setup, Docker | Service dependencies |
| Manifest scripts.dev/start/serve | Local Development | Dev command |
| Manifest scripts.test | Testing | Test command |
| Manifest scripts.lint/format | Lint and Format | Lint/format commands |
| Makefile/Justfile targets | Common Tasks | Available commands |
| Migration config (alembic.ini, prisma/) | Database | Migration commands |
| Dockerfile | Docker | Build/run commands |
| .github/workflows/ deploy steps | Release and Deployment | Deploy workflow |
| CI workflow test steps | Testing | CI test configuration |
| README.md sections | All sections | Cross-reference for accuracy |

---

## Quality Rubric

The self-validation pass checks these criteria:

- **COMPLETENESS:** Every Required Section is present. Setup has numbered
  steps. Testing has at least one command. Common Tasks table has at least
  one row.
- **TRUTHFULNESS:** Every command comes from a manifest script, Makefile
  target, CI config, or README — not from general framework knowledge.
  All cited file paths exist (verified by Glob). Commands match their
  stated source (e.g., if it says "from package.json scripts.test", the
  command matches what's actually in package.json).
- **CONCISENESS:** No explanations of what tools do (the reader knows).
  No "best practice" recommendations. Just commands and their sources.
  No section exceeds 25 lines.
- **DETERMINISM:** Sections appear in the order listed above. Command
  format uses backtick code blocks consistently. Source citations use
  consistent `(from [file])` format.

---

## Anti-Patterns

DO NOT produce output like this:

- `Run npm install to install dependencies.`
  → Don't assume npm. Check the lockfile. If pnpm-lock.yaml exists:
  `Run pnpm install (from pnpm-lock.yaml presence)`
- `Start the development server with npm run dev.`
  → Check the actual script name. It might be `start`, `serve`, or `develop`.
  Always cite: `(from package.json scripts.dev)`
- `You can debug using Chrome DevTools.`
  → Only include if there's a debug config or script. Don't recommend tools
  not configured in the repo.
- `To deploy, push to main and the CI pipeline will handle it.`
  → Only if a CI workflow file confirms this. Cite the workflow file.
- Inventing commands that don't exist in any manifest, Makefile, or config.
- Recommending workflows based on framework conventions when the repo might
  use different conventions.
- Including setup steps from a different framework version or conflicting
  with README instructions.
