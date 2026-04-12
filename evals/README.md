# Archeia Evaluation Framework

This directory contains the experimental harness for measuring whether Archeia-generated
documentation materially improves AI coding agent performance on real, large codebases.
The study is a controlled within-subject experiment: the same tasks and repos are evaluated
under multiple documentation conditions so that per-task variance can be differenced out.

---

## Goals

The central research question is:

> **Does Archeia-generated documentation reduce the tokens and tool calls an AI agent needs
> to complete coding tasks, while increasing the quality of its output?**

Secondary questions:

- Does the benefit scale with codebase size and complexity?
- Is the architecture-first bundle (l1) sufficient, or does the full colocated bundle (l2) add
  meaningful lift?
- Which task categories benefit most — exploration/ask tasks, planning tasks, or implementation
  tasks?
- Is there a measurable difference on `arq` (tiny, flat codebase), which serves as a negative
  control?

---

## Study Design

### Conditions

Three documentation conditions are evaluated per (repo, task, trial) triple.

| ID | Label | What the agent sees |
|----|-------|---------------------|
| `l0` | Native Baseline | The repo's existing docs left exactly as they are. For repos that already have `AGENTS.md`/`CLAUDE.md`, this is a non-trivial baseline. For `arq` (no native agent docs) it collapses to a bare-repo baseline. |
| `l1` | Architecture Bundle | All existing agent docs are removed and replaced with the Archeia-generated `AGENTS.md`, `CLAUDE.md`, and the `.archeia/` directory tree (architecture diagrams, entity maps, state machines, etc.). |
| `l2` | Full Archeia | Everything in l1 plus colocated per-module `README.md` files and per-module `AGENTS.md` files placed next to the code they describe. |

The condition applier always starts from a pristine git worktree at the pinned commit, removes
every known Archeia doc path, then copies the selected doc sets in. This ensures l0 is actually
the repo's native state, not a doc-stripped state.

### Repos

Five repos are evaluated, chosen to represent a range of codebase sizes, languages, and
structural patterns.

| ID | GitHub repo | Language | LOC | Complexity | Role |
|----|------------|----------|-----|------------|------|
| `polar` | polarsource/polar | Python + TypeScript | 529 000 | complex | Largest; cross-module plan/implement tasks |
| `daily-api` | dailydotdev/daily-api | TypeScript | 301 000 | medium | Large API; convention-following tasks |
| `mitmproxy` | mitmproxy/mitmproxy | Python + TypeScript | 160 000 | medium | **Pilot repo**; has tests and lint |
| `relay` | AgentWorkforce/relay | multi | 69 000 | medium | Has hand-written `ARCHITECTURE.md`; Archeia-vs-human comparison |
| `arq` | python-arq/arq | Python | 6 000 | flat | **Negative control**; codebase fits in context |

All repos are pinned at specific commits to ensure fully reproducible runs. The pinned clones
live at `/Users/hugopeck/archeia-archive/packages/experiments/repos/clones/`.

### Tasks

Fifty tasks are defined — ten per repo — organized into five categories:

| Category | Count per repo | What it tests |
|----------|---------------|---------------|
| `ask-complex` | 2 | Agent explains a non-obvious subsystem or flow |
| `plan-complex` | 2 | Agent designs an approach for a cross-module change |
| `implement-simple` | 2 | Agent adds a small field, flag, or guard |
| `implement-moderate` | 2 | Agent adds a new endpoint, handler, or routine |
| `implement-complex` | 2 | Agent implements a cross-cutting change with side-effects |

Tasks are authored in Phase 2 against the pinned commits. Each task has:
- `prompt` — a realistic user request that deliberately avoids naming specific files.
- `ground_truth` — the correct answer or reference implementation the judge uses.
- `acceptance_criteria` — an explicit list of pass/fail checks.
- `expected_modules_read` — broad module hints (not file-level spoilers).
- `commands` — optional task-level test/lint overrides.
- `metadata` — `difficulty`, `output_type`, `primary_surface`, `doc_sensitivity`, `verification_scope`.

### Trials

Each (repo, task, condition) cell is intended to be run multiple times. Trial numbering starts
at 1. Multiple trials let the analysis compute means and confidence intervals for stochastic
agent outputs.

### Scale

A full study across 5 repos × 50 tasks × 3 conditions × N trials is large. The framework is
designed to be run incrementally — one cell at a time — so Phase 4 pilots on `mitmproxy` alone
before committing to the full matrix.

---

## Five Phases

### Phase 1 — Infrastructure (this code)

Everything in this directory: configuration schema, condition applier, agent runner, metric
collectors, LLM judge, aggregator, and report generator. Also includes the unit test suite.

### Phase 2 — Preparation

Task files (`evals/config/tasks/<repo-id>/`) and bundle specs (`evals/config/bundles/`) are
authored and reviewed before any Archeia pipeline run. Tasks must be grounded at the pinned
commits. Bundle specs lock the expected Archeia pipeline outputs (skill order, expected files,
copy rules, validation settings) that Phase 3 will produce.

Phase 2 is complete when every repo has exactly 10 grounded tasks with `id`, `repo_id`,
`category`, `prompt`, `ground_truth`, and `acceptance_criteria` — and every repo has a bundle
spec with `pipeline_order`, `expected_outputs`, and `copy_rules`.

### Phase 3 — Canonical Archeia generation

The real Archeia skill pipeline is run against each pinned repo clone and the outputs are
captured under `evals/archeia-output/<repo-id>/`. The expected layout per repo is:

```
evals/archeia-output/<repo-id>/
  AGENTS.md
  CLAUDE.md
  .archeia/
    Architecture.md
    Entities.json          (if entity model evidence found)
    StateMachine.json      (if state machine evidence found)
    Containers.json        (if container evidence found)
    Components.json        (if component evidence found)
  colocated-readmes/
    manifest.json          (source → target path mapping)
    <generated README files>
  colocated-agents/
    manifest.json
    <generated AGENTS.md files>
```

Manual draft docs must not be placed here — `archeia-output/` is a Phase 3 output only. The
`manifest.json` files drive the condition applier's colocated copy rules.

Use the helper scripts to standardize this phase:

```bash
python3 evals/scripts/prepare_phase3_workspace.py --repo-id polar --work-root /tmp/archeia-phase3
# start a subagent in the reported worktree and paste .archeia-eval/subagent-packet.md
python3 evals/scripts/capture_phase3_bundle.py --repo-id polar --worktree /tmp/archeia-phase3/polar --force
```

See `evals/PHASE3_RUNBOOK.md` for the packet-based operator workflow.

### Phase 4 — Pilot eval runs

`mitmproxy` is used as the pilot repo because it is mid-sized, has both tests (`uv run pytest`)
and lint (`uv run ruff check .`), and has known-good Archeia output. The full workflow is
validated on a handful of tasks across all three conditions before broadening.

### Phase 5 — Full eval runs and reporting

The study is executed across all repos, conditions, and trials. Results land in
`evals/results/raw/`, are aggregated and reported via the analysis scripts, and
the full `evals/results/` tree is committed to git as evaluation evidence.

---

## Repository Layout

```
evals/
  common.py                # shared utilities: I/O, subprocess, stats, metric path extraction
  __init__.py

  config/
    conditions.yaml        # l0 / l1 / l2 condition definitions and doc_sets
    repos.yaml             # repo registry: pinned commits, source paths, commands
    bundles/               # Phase 2 bundle specs (per-repo pipeline briefs)
      README.md
      arq.yaml
      daily-api.yaml
      mitmproxy.yaml
      polar.yaml
      relay.yaml
    tasks/
      README.md            # task authoring guide
      task-template.yaml   # canonical task schema with all fields
      arq/                 # 10 task files
      daily-api/           # 10 task files
      mitmproxy/           # 10 task files
      polar/               # 10 task files
      relay/               # 10 task files

  harness/
    runner.py              # end-to-end orchestration: worktree → condition → agent → judge → result
    condition_applier.py   # copies/removes doc sets in the worktree
    claude_runner.py       # wraps the agent CLI and captures its transcript

  collectors/
    metrics.py             # parses agent transcripts for token, tool, and timing metrics
    code_quality.py        # runs test/lint commands and computes lint delta from baseline

  judges/
    llm_judge.py           # builds rubric prompts, calls LLM judge, parses JSON scores

  analysis/
    aggregate.py           # statistical aggregation across conditions/repos/categories
    report.py              # markdown report generator

  archeia-output/          # Phase 3 outputs only — do not manually edit
    README.md
    arq/
    daily-api/
    mitmproxy/
    polar/
    relay/

  results/
    raw/                   # one JSON file per (repo, task, condition, trial)
    reports/               # aggregate.json + markdown reports

  tests/
    test_framework.py      # unit tests for condition applier, metrics, and aggregation
    run.sh                 # shortcut: python -m unittest discover
```

---

## How a Single Run Works

The runner (`harness/runner.py`) orchestrates these steps in order:

1. **Load config.** Read `repos.yaml` and the task YAML. Validate repo_id match.

2. **Create git worktree.** `git worktree add --detach <destination> <pinned-commit>` on the
   pinned source clone. This gives an isolated, clean checkout without touching the original.

3. **Apply condition.** The condition applier:
   - For l0: leaves the worktree untouched (`keep_existing_docs: true`).
   - For l1/l2: removes all known Archeia doc paths (root docs + `.archeia/` + colocated files
     from manifests), then copies the selected doc sets from `evals/archeia-output/<repo-id>/`.

4. **Commit condition state.** `git add -A && git commit` with a neutral message so the agent
   has a clean working tree and the diff after the run reflects only its changes.

5. **Baseline lint (pre-agent).** Runs the repo's lint command before the agent touches anything
   to establish a baseline finding count for the delta calculation.

6. **Run agent.** Invokes the agent CLI (default: `claude --output-format json -p <prompt>`) in
   the worktree directory. Stdout is written to `.archeia-eval/conversation.json` if the agent
   does not produce it automatically. The agent has a 900-second timeout by default.

7. **Collect metrics.** Parses the transcript JSON for token counts, tool call counts, timing
   timestamps, and the exploration-to-action ratio.

8. **Capture git diff.** `git diff --no-ext-diff` records what the agent actually changed.

9. **Run code quality checks (post-agent).** Runs test and lint commands. Computes
   `lint_delta = post_findings − pre_findings`.

10. **Judge.** An LLM judge receives the task prompt, ground truth, acceptance criteria, agent
    response, git diff, lint results, and efficiency metrics. It returns a structured JSON score
    (see Judging section below).

11. **Write result.** The full payload is written to
    `evals/results/raw/<repo-id>/<task-id>/<condition-id>/trial-<n>.json`.

12. **Clean up worktree.** `git worktree remove --force` unless `--keep-worktree` was passed.

If any step fails, the runner catches the exception and writes a result file with
`status: failed` and an `error` field describing the exception. The worktree is always
cleaned up in the `finally` block. This ensures every cell produces a result file even when
the agent times out, tests hang, or the judge crashes.

---

## Metrics Collected

### Efficiency metrics (from agent transcript)

| Metric | Description |
|--------|-------------|
| `total_tokens` | Peak total token count found in the transcript |
| `input_tokens` | Peak input token count |
| `output_tokens` | Peak output token count |
| `tool_call_count` | Total tool invocations across the session |
| `exploration_calls` | Calls to read/grep/glob tools |
| `action_calls` | Calls to write/edit/multiedit/apply_patch tools |
| `exploration_to_action_ratio` | `exploration_calls / action_calls` — higher means more reading before writing |
| `time_to_completion_seconds` | Elapsed time from first to last timestamp in the transcript |
| `time_to_first_edit_seconds` | Time from session start to first action-class tool call |

The metric collector walks the entire transcript JSON tree, handles both single-object and
JSONL formats, and normalizes tool names to lowercase snake_case.

### Code quality metrics (from test/lint execution)

| Metric | Description |
|--------|-------------|
| `lint_findings` | Number of non-empty lines in lint output after the agent run |
| `lint_baseline_findings` | Same metric before the agent run |
| `lint_delta` | `lint_findings − lint_baseline_findings` (negative = improvement, positive = regression) |
| `tests` | Full subprocess result (exit code, stdout, stderr) from the test command |

Code quality checks are optional. A repo or task with `null` test/lint commands will have
`null` entries in the output rather than erroring.

### Judge score (from LLM judge)

The LLM judge scores each run 0–100 across four equally weighted 25-point dimensions:

**For `ask-*` tasks:**
1. Correctness — factual accuracy against ground truth
2. Completeness — covers all relevant systems and caveats
3. Evidence alignment — cites or reflects the repo-grounded flow
4. Communication quality — organized, concise, and directly useful

**For `plan-*` tasks:**
1. Correctness — technically sound approach
2. Completeness — affected modules, sequencing, and risks covered
3. Convention fit — follows the repo's apparent patterns
4. Actionability — specific enough to implement

**For `implement-*` tasks:**
1. Correctness — change solves the task
2. Completeness — includes all required code-path updates
3. Convention fit — matches project structure and patterns
4. Verification — test/lint outcomes support the change

The judge response schema:
```json
{
  "total_score": 0,
  "dimension_scores": {
    "correctness": 0,
    "completeness": 0,
    "convention_fit": 0,
    "verification_or_communication": 0
  },
  "summary": "short paragraph",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "confidence": "low|medium|high"
}
```

The judge is also configurable via `--judge-command-json` so a different model or provider can
be substituted.

---

## Statistical Analysis

The aggregator (`analysis/aggregate.py`) produces a single `aggregate.json` with:

- **Overall** summary across all results.
- **By condition** (`l0`, `l1`, `l2`).
- **By repo** (five repos).
- **By category** (`ask-complex`, `plan-complex`, `implement-*`).

For each slice and metric, it reports: `mean`, `ci95_lower`, `ci95_upper`, `stddev`, `min`,
`max`, and `count`.

**Pairwise comparisons** use the Wilcoxon signed-rank test on paired differences (matched by
`repo_id::task_id::trial`). The default pairs are:
- `l0` vs `l1` on `judge.total_score`
- `l0` vs `l2` on `judge.total_score`
- `l0` vs `l1` on `metrics.total_tokens`
- `l0` vs `l2` on `metrics.total_tokens`

The Wilcoxon test is appropriate here because:
- Scores are not normally distributed (bounded 0–100, potentially bimodal).
- Sample sizes may be small (N ≈ number of tasks × trials per cell).
- It is sensitive to paired direction of change without requiring parametric assumptions.

The report generator (`analysis/report.py`) formats the aggregate JSON into a markdown report.

---

## Assumptions

1. **Pinned commits are stable.** The same commit hash always produces the same worktree.
   External dependency changes (package registries, network calls) are not controlled for.

2. **LLM judge is a valid proxy.** The judge's four-dimension rubric is assumed to correlate
   with human assessment of agent output quality. This has not been formally validated against
   human raters.

3. **Token count is a valid efficiency proxy.** Lower tokens for equivalent quality indicates
   the documentation helped the agent orient faster. This conflates context-window efficiency
   with actual agent reasoning quality.

4. **The exploration-to-action ratio is meaningful.** A higher ratio suggests the agent read
   more before acting, which may indicate better codebase understanding — or may indicate
   confusion. Interpretation requires pairing with quality scores.

5. **Condition application is transparent to the agent.** The agent is given only the task
   prompt. It has no awareness of which condition it is in. Prompt text is identical across
   conditions for the same task.

6. **Lint finding count is a reasonable quality signal.** The proxy `len(non-empty-output-lines)`
   is a coarse measure. Some linters produce multi-line findings; others produce one line per
   finding. Repos with `null` lint commands produce no signal.

7. **Trials are independent.** No state is shared between trials. The worktree is created fresh
   from the pinned commit for every run.

---

## Limitations

- **No human rater validation.** The judge is an LLM evaluating LLM output. Systematic biases
  in the judge (e.g., rewarding verbosity, or being fooled by confident-sounding wrong answers)
  will affect all conditions equally but may mask absolute quality differences.

- **Single-machine execution.** Results depend on the `claude` CLI version, API quotas, and
  system load at run time. No containerization or hermetic build environment is enforced.

- **Token metrics are heuristic.** The collector takes the maximum observed value for each
  token type across all dict nodes in the transcript, which may over-count if the transcript
  contains cumulative totals.

- **Colocated manifests are empty stubs.** Until Phase 3 completes, `manifest.json` files
  under `archeia-output/*/colocated-*/` are empty arrays. l2 condition runs before Phase 3
  will behave identically to l1.

- **arq is probably too small.** At 6 000 LOC, `arq` fits comfortably in a model's context
  window. Archeia documentation may provide no measurable benefit, and this repo is included
  specifically as a negative control to validate that the methodology can detect null effects.

- **Wilcoxon requires paired data.** If some (task, trial) pairs produce results for one
  condition but not another (e.g., a timeout or agent crash), those pairs are excluded from the
  pairwise test. Small N after exclusions reduces statistical power.

- **No cross-repo randomization.** Each repo uses a fixed set of 10 tasks. If task difficulty
  happens to be unevenly distributed across conditions within a repo, it will appear as a
  condition effect. The Phase 2 task authoring process is designed to mitigate this by keeping
  prompts identical across conditions.

- **No built-in parallel execution.** The runner is single-threaded per cell. Running the full
  study matrix (5 repos × 50 tasks × 3 conditions × N trials) requires external orchestration.
  30 cells per repo can be launched in parallel; the runner handles git lock contention via
  retries with jittered backoff.

---

## Expected Results

Based on the study design, the following outcomes would be consistent with a positive result:

- `l1` and `l2` show higher `judge.total_score` than `l0` across `ask` and `plan` tasks,
  with the largest deltas on `polar` and `daily-api` (most complex repos).
- `l1` and `l2` show lower `metrics.total_tokens` than `l0` for equivalent task categories,
  as the structured docs help the agent orient without exhaustive exploration.
- `metrics.exploration_to_action_ratio` decreases under Archeia conditions — the agent reads
  fewer modules before making its first edit because it has a map.
- `metrics.time_to_first_edit_seconds` decreases under Archeia conditions.
- `arq` shows no statistically significant difference across conditions (negative control).
- `relay` shows `l1`/`l2` competitive with or better than `l0`, even though `l0` includes a
  human-authored `ARCHITECTURE.md` — this would validate Archeia-generated docs against
  hand-written equivalents.
- `l2` shows incremental lift over `l1` primarily on `implement-complex` tasks where finding
  the right module to edit benefits from colocated guidance.

A null result — no detectable difference — would suggest either that the LLM judge rubric is
too noisy, that the tasks are insufficiently sensitive to documentation, or that Archeia docs do
not provide information the model could not derive from the codebase alone.

---

## Quick Start

**Run unit tests:**
```bash
python3 -m unittest discover -s evals/tests -p 'test_*.py'
```

**Dry-run a single cell (no agent invoked):**
```bash
python3 evals/harness/runner.py \
  --repo-id mitmproxy \
  --condition l1 \
  --task-config evals/config/tasks/mitmproxy/mitmproxy-ask-complex-01.yaml \
  --trial 1 \
  --dry-run
```

**Run a single eval cell:**
```bash
python3 evals/harness/runner.py \
  --repo-id mitmproxy \
  --condition l1 \
  --task-config evals/config/tasks/mitmproxy/mitmproxy-ask-complex-01.yaml \
  --trial 1
```

**Run without LLM judging (faster iteration):**
```bash
python3 evals/harness/runner.py \
  --repo-id mitmproxy \
  --condition l0 \
  --task-config evals/config/tasks/mitmproxy/mitmproxy-implement-simple-01.yaml \
  --trial 1 \
  --skip-judge
```

**Keep the worktree for inspection after the run:**
```bash
python3 evals/harness/runner.py \
  --repo-id arq \
  --condition l2 \
  --task-config evals/config/tasks/arq/arq-implement-moderate-01.yaml \
  --trial 1 \
  --keep-worktree \
  --work-root /tmp/archeia-eval-debug
```

**Override the agent command (e.g., use a different CLI):**
```bash
python3 evals/harness/runner.py \
  --repo-id mitmproxy \
  --condition l1 \
  --task-config evals/config/tasks/mitmproxy/mitmproxy-ask-complex-01.yaml \
  --trial 1 \
  --agent-command-json '["my-agent", "--prompt", "{prompt}"]'
```

**Aggregate collected results:**
```bash
python3 evals/analysis/aggregate.py --results-root evals/results/raw
```

**Generate a markdown report:**
```bash
python3 evals/analysis/report.py --aggregate evals/results/reports/aggregate.json
```

Commit the updated `evals/results/` tree after refreshing either output.

**Inspect transcript metrics for a saved run:**
```bash
python3 evals/collectors/metrics.py path/to/.archeia-eval/conversation.json
```

**Re-judge a saved run payload:**
```bash
python3 evals/judges/llm_judge.py \
  --task evals/config/tasks/mitmproxy/mitmproxy-ask-complex-01.yaml \
  --run-payload evals/results/raw/mitmproxy/.../trial-1.json
```

---

## Configuration Notes

**YAML parsing.** All `*.yaml` config files are written in JSON-compatible YAML so they parse
with Python's stdlib `json` module when `PyYAML` is not installed. Regular YAML also works if
`PyYAML` is available.

**Repo source paths.** `repos.yaml` points to pinned clones at
`/Users/hugopeck/archeia-archive/packages/experiments/repos/clones/`. These are not vendored
in this repo. Phase 3 requires them to be present.

**Timeouts.** Defaults are 900 s for the agent, 300 s for the judge, and 600 s for code quality
checks. All are configurable via CLI flags. Timeouts are handled gracefully: `run_command`
catches `subprocess.TimeoutExpired` and records `timed_out: true` in the result dict, and
`orchestrate_run` catches all exceptions to always produce a result file with `status: failed`
rather than crashing with no output.

**Results path.** Default results root is `evals/results/raw/`. Results are written to
`<results-root>/<repo-id>/<task-id>/<condition-id>/trial-<n>.json`.

**Agent and judge commands.** Both accept a `--*-command-json` flag expecting a JSON array of
strings where `{prompt}`, `{cwd}`, and `{transcript}` are substituted at runtime. This makes
the harness model-agnostic.
