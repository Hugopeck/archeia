# Phase 4 Resume Prompt

Resume Phase 4 exactly as planned in `evals/PHASE4_RUNBOOK.md` and the repo context.

## Current status

- Phase 4 uses **one agent per cell**, with **one repo at a time** in batches of **30 parallel cells**.
- The eval model is **Haiku** for every `runner.py` invocation.
- `polar` is already complete: **30/30** result files exist under `evals/results/raw/polar/`.
- Those `polar` partial results are already committed.
- Remaining repos to run: **`daily-api` → `mitmproxy` → `relay` → `arq`**.
- Aggregate/report outputs have **not** been generated yet.

## Rules to preserve

- Do **not** run multiple cells in a loop inside one long-lived agent.
- Do **not** switch away from `--model haiku`.
- Do **not** re-run completed `polar` cells unless a specific retry is required.
- Follow the agent-oriented runbooks already present in:
  - `evals/PHASE3_RUNBOOK.md`
  - `evals/PHASE4_RUNBOOK.md`

## What to do

1. Confirm the repo is clean and inspect current results under `evals/results/raw/`.
2. Resume Phase 4 from the next repo batch: **`daily-api`**.
3. For each remaining repo, launch **30 isolated cells** in parallel:
   - 10 tasks × 3 conditions (`l0`, `l1`, `l2`)
   - 1 trial each
   - `--model haiku`
4. After each repo batch, verify:
   - exactly **30** `trial-1.json` files for that repo
   - no failed/error statuses
   - retry only the failed cells, still using one fresh agent per cell
5. After all remaining repos complete, verify there are **150** total `trial-1.json` files.
6. Generate:
   - `evals/results/reports/aggregate.json`
   - `evals/results/reports/pilot-report.md`
7. Commit the newly produced Phase 4 results and report artifacts.

## Commands and references

Use the exact execution/verification/report commands from `evals/PHASE4_RUNBOOK.md`.
If Phase 3 packet behavior is needed for any reason, use `evals/PHASE3_RUNBOOK.md`.

## Expected end state

- `evals/results/raw/` contains **150** completed result files
- no remaining failed cells
- aggregate + markdown report generated
- all new artifacts committed
