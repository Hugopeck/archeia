# Eval Smoke Tests

Lightweight checks that exercise the eval harness end-to-end *without*
touching `evals/results/` or `evals/archeia-output/` and without invoking
the agent (so no API cost).

Used as a verification gate during path/namespace migrations — e.g. the
Phase 1 monorepo bootstrap that restructured bundles into
`.archeia/codebase/`. The purpose is to confirm the harness still loads
config, still copies bundles into a worktree, and still produces the
expected file layout under the new paths.

## What it runs

1. **Unit tests** — `python3 -m unittest discover -s evals/tests -p 'test_*.py'`
2. **Dry-run** — `evals/harness/runner.py --dry-run` on one arq task
3. **Real `apply_condition`** — imports `evals.harness.condition_applier`
   and copies the real arq bundle into a scratch worktree, asserting the
   expected `.archeia/codebase/**` files land where the standard says.

No `claude` agent invocation, no `evals/results/` writes.

## Where output goes

- **`evals/smoke/runs/<timestamp>/`** — logs and JSON summary for each run.
  Gitignored.
- **`/tmp/archeia-smoke/<timestamp>/`** — scratch worktree for the real
  `apply_condition` check. Outside the repo; cleaned up by the driver on
  success, preserved on failure for inspection.

## Running

```bash
bash evals/smoke/run_smoke.sh
```

Exits non-zero on any failed step. Writes a `summary.json` with per-step
results.
