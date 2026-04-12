#!/usr/bin/env bash
# Phase 1 smoke test — runs from repo root.
set -u

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="evals/smoke/runs/$TS"
SCRATCH="/tmp/archeia-smoke/$TS"
mkdir -p "$RUN_DIR" "$SCRATCH"

UNIT_LOG="$RUN_DIR/01-unit-tests.log"
DRY_LOG="$RUN_DIR/02-runner-dry-run.log"
APPLY_LOG="$RUN_DIR/03-apply-condition.log"
APPLY_SUMMARY="$RUN_DIR/03-apply-condition.summary.json"
FINAL_SUMMARY="$RUN_DIR/summary.json"

status_unit=skipped
status_dry=skipped
status_apply=skipped

echo "[1/3] Running unit tests -> $UNIT_LOG"
if python3 -m unittest discover -s evals/tests -p 'test_*.py' > "$UNIT_LOG" 2>&1; then
  status_unit=pass
  echo "      pass"
else
  status_unit=fail
  echo "      FAIL (see log)"
fi

echo "[2/3] Runner dry-run on arq task -> $DRY_LOG"
if python3 evals/harness/runner.py \
    --repo-id arq \
    --condition l1 \
    --task-config evals/config/tasks/arq/arq-ask-complex-01.yaml \
    --trial 1 \
    --dry-run \
    --work-root "$SCRATCH/work" \
    --results-root "$RUN_DIR/runner-results" \
    > "$DRY_LOG" 2>&1; then
  status_dry=pass
  echo "      pass"
else
  status_dry=fail
  echo "      FAIL (see log)"
fi

echo "[3/3] apply_condition on real arq bundle -> $APPLY_LOG"
if python3 evals/smoke/apply_condition_check.py \
    --repo-id arq \
    --condition l1 \
    --scratch "$SCRATCH/apply" \
    --summary "$APPLY_SUMMARY" \
    > "$APPLY_LOG" 2>&1; then
  status_apply=pass
  echo "      pass"
else
  status_apply=fail
  echo "      FAIL (see log)"
fi

overall=pass
[ "$status_unit" = fail ] && overall=fail
[ "$status_dry" = fail ] && overall=fail
[ "$status_apply" = fail ] && overall=fail

cat > "$FINAL_SUMMARY" <<JSON
{
  "timestamp": "$TS",
  "overall": "$overall",
  "steps": {
    "unit_tests": "$status_unit",
    "runner_dry_run": "$status_dry",
    "apply_condition": "$status_apply"
  },
  "logs_dir": "$RUN_DIR",
  "scratch_dir": "$SCRATCH"
}
JSON

echo
echo "=== summary ($overall) ==="
cat "$FINAL_SUMMARY"

if [ "$overall" = pass ]; then
  # Only clean scratch on success; on failure we keep it for inspection.
  rm -rf "$SCRATCH"
fi

[ "$overall" = pass ] || exit 1
