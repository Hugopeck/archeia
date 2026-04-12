# Phase 4 Runbook — Eval Matrix Execution

This runbook is for the orchestrator agent running the full Phase 4 eval
matrix. It covers prerequisites, cell execution, batch verification, and
report generation.

**Matrix:** 5 repos × 10 tasks × 3 conditions × 1 trial = 150 cells

**Isolation rule:** Each cell gets its own background agent running a single
`runner.py` invocation. Do not loop multiple tasks inside one agent — context
accumulated from prior task prompts and file reads contaminates subsequent
runs. `runner.py` already spawns a fresh `claude` subprocess per cell; the
same isolation must be maintained at the agent level.

**Execution order:** Process repos one at a time (30 parallel agents per
repo). This limits concurrent git worktree operations to a single source repo
and makes per-repo failure inspection tractable.

All commands run from the project root (the directory containing `evals/`).

---

## Prerequisites

Run these checks before launching any cells. Stop if any fails.

```bash
# Agent CLI available
which claude && claude --version

# Unit tests pass
python3 -m unittest discover -s evals/tests -p 'test_*.py'

# All 5 Phase 3 bundles present (bundle-manifest.json exists per repo)
for repo in polar daily-api mitmproxy relay arq; do
  python3 -c "
import json; from pathlib import Path
b = Path('evals/archeia-output/$repo')
assert (b / 'bundle-manifest.json').exists(), 'missing bundle-manifest.json'
print('$repo: ok')
"
done

# Task files present (expect 10 per repo)
for repo in polar daily-api mitmproxy relay arq; do
  count=$(ls evals/config/tasks/$repo/*.yaml 2>/dev/null | wc -l | tr -d ' ')
  echo "$repo: $count task files"
done
```

Dry-run smoke test (validates harness config without running the agent):

```bash
python3 evals/harness/runner.py \
  --repo-id polar \
  --condition l0 \
  --task-config evals/config/tasks/polar/polar-ask-complex-01.yaml \
  --trial 1 \
  --model haiku \
  --dry-run \
  --work-root /tmp/archeia-phase4
```

A successful dry-run prints a JSON payload with `status: dry_run` and no errors.

---

## Cell Execution

Each cell is one background agent running exactly this command:

```bash
python3 evals/harness/runner.py \
  --repo-id <repo> \
  --condition <l0|l1|l2> \
  --task-config evals/config/tasks/<repo>/<task>.yaml \
  --trial 1 \
  --model haiku \
  --work-root /tmp/archeia-phase4
```

The runner:
1. Creates a git worktree from the archived pinned clone at the pinned commit
2. Applies the condition (l0=keep existing, l1=root+archeia bundle, l2=full bundle)
3. Commits condition state so the eval agent sees a clean working tree
4. Spawns `claude --model haiku` with the task prompt and EVAL_SYSTEM_PROMPT
5. Collects token and tool-call metrics from the transcript
6. Spawns a `claude` judge to score 4 dimensions (0–100 total)
7. Writes `evals/results/raw/<repo>/<task>/<condition>/trial-1.json`
8. Removes the worktree

**Execution order — one repo at a time:**

1. polar (30 cells)
2. daily-api (30 cells)
3. mitmproxy (30 cells)
4. relay (30 cells)
5. arq (30 cells)

Within each repo, launch all 30 cells simultaneously as background agents.

---

## Batch Verification

After each repo batch completes, verify before moving to the next:

```bash
# Count completed cells (expect 30)
find evals/results/raw/<repo> -name 'trial-1.json' | wc -l

# Check for failures
python3 -c "
import json; from pathlib import Path
failed = []
for f in Path('evals/results/raw/<repo>').rglob('trial-1.json'):
    d = json.loads(f.read_text())
    if d['status'] != 'completed':
        failed.append(f'{f}: {d[\"status\"]}')
print(f'Failed: {len(failed)}')
for x in failed: print(f'  {x}')
"
```

**Retry protocol:** For any failed cell, launch a new single-agent with the
same runner.py command. A cell may fail due to agent timeout, worktree
contention, or judge error — inspect `agent_run.stderr` or `judge.raw_output`
in the result JSON to diagnose.

Timeout tuning:

| Flag | Default | When to increase |
|------|---------|-----------------|
| `--agent-timeout` | 900s | Complex implement tasks on large repos (polar, daily-api) may need 1200–1800s |
| `--judge-timeout` | 300s | Rarely needed |
| `--quality-timeout` | 600s | Repos with slow test suites (relay `npm test` consistently exceeds 600s) |

**Concurrency notes (learned from the first full run):**

- **Git lock contention.** 30 simultaneous `git worktree add` calls on the same
  source repo will race on git's internal lock. `create_worktree` now retries
  with jittered exponential backoff (up to 5 attempts), which resolves most
  contention. No pre-creation step is needed.

- **Subprocess timeouts are non-fatal.** `run_command` catches
  `subprocess.TimeoutExpired` and records the timeout in the result dict
  (`timed_out: true`) instead of crashing the runner. The runner's
  `orchestrate_run` also wraps the full pipeline in a try/except so any
  unexpected exception produces a `status: failed` result file rather than
  leaving no output.

- **Direct bash vs. agent wrappers.** When the orchestrator is an AI agent,
  its internal Bash tool may impose a shorter timeout than `--agent-timeout`.
  For implement tasks expected to exceed 10 minutes, launch runner.py as a
  direct background shell command rather than inside a subagent. A helper
  script pattern works well:

  ```bash
  # Generate all 30 commands, then run them in parallel:
  for task in evals/config/tasks/<repo>/*.yaml; do
    for cond in l0 l1 l2; do
      echo "python3 evals/harness/runner.py --repo-id <repo> --condition $cond \
        --task-config $task --trial 1 --model haiku --agent-timeout 1800 \
        --work-root /tmp/archeia-phase4 &"
    done
  done | bash
  wait
  ```

---

## Full Matrix Verification

After all 5 repo batches complete:

```bash
# Total completed cells (expect 150)
find evals/results/raw -name 'trial-1.json' | wc -l

# Failures across all repos
python3 -c "
import json; from pathlib import Path
failed = []
for f in Path('evals/results/raw').rglob('trial-1.json'):
    d = json.loads(f.read_text())
    if d['status'] != 'completed':
        failed.append(f'{f.relative_to(\"evals/results/raw\")}: {d[\"status\"]}')
print(f'Total failed: {len(failed)} / 150')
for x in failed: print(f'  {x}')
"

# Quick score summary
python3 -c "
import json; from pathlib import Path
rows = []
for f in sorted(Path('evals/results/raw').rglob('trial-1.json')):
    d = json.loads(f.read_text())
    rows.append((
        d.get('repo_id','?'),
        d.get('condition_id','?'),
        d.get('task',{}).get('id','?'),
        d.get('judge',{}).get('total_score','?'),
        d.get('metrics',{}).get('total_tokens','?'),
    ))
for r in rows:
    print('\t'.join(str(x) for x in r))
"
```

---

## Report Generation

```bash
# Aggregate all results
python3 evals/analysis/aggregate.py \
  --results-root evals/results/raw \
  --output evals/results/reports/aggregate.json

# Generate markdown report
python3 evals/analysis/report.py \
  --aggregate evals/results/reports/aggregate.json \
  --output evals/results/reports/pilot-report.md
```

The report includes per-condition means and 95% CIs for judge scores and token
counts, per-category breakdowns, and Wilcoxon signed-rank p-values for
l0→l1 and l0→l2 pairwise comparisons.

---

## Healthy vs. Stop Signals

**Healthy (proceed to Phase 5):**
- Judge scores trend: l2 ≥ l1 ≥ l0 across most task categories
- Token counts: l1/l2 ≤ l0 for ask and plan tasks
- Implement tasks produce non-trivial diffs under all conditions
- No systematic harness failures

**Stop (investigate before proceeding):**
- `status: failed` in result files — harness bug, check `agent_run.stderr`
- `condition_application.copied_paths: []` for l1/l2 — bundle not being applied
- `agent_run.stdout` empty — CLI invocation broken
- Judge `status: failed` on most runs — judge prompt or CLI broken
- Metrics all null — transcript format mismatch

---

## Invariants

- Every cell is an isolated agent with no shared context
- `--model haiku` on every runner.py invocation
- Worktrees are created and destroyed per cell (no reuse across conditions)
- Results are never hand-edited
- Re-runs use the same trial number as the original (overwrite, not append)
