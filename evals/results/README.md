# Eval Results (Historical)

This directory contains frozen results from eval runs that predate the
Archeia Standard monorepo migration. Do not rewrite these files.

## Contents

- `raw/<repo>/<task>/<condition>/trial-N.json` — per-trial raw output from
  each Phase 3/4 eval run. These JSONs record the exact file paths, prompts,
  and model responses captured at run time.
- `reports/` — aggregated reports generated from `raw/`.

## Path layout note

Files under `raw/` reference the flat pre-migration `.archeia/` layout
(`.archeia/Architecture.md`, `.archeia/System.json`, etc.) because that was
the layout when those runs executed. The canonical output bundles under
`evals/archeia-output/` were rewritten to the new `.archeia/codebase/`
layout as part of the monorepo bootstrap, but the historical run records
here are intentionally left untouched — they are a frozen audit trail of
what happened at the time. If you need to compare against current skill
output, re-run the eval harness against the new monorepo; that produces
new result files under new paths without disturbing these.

See `evals/archeia-output/README.md` for the migration notes covering the
bundle restructure.
