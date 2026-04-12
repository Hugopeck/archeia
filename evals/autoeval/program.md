# Autoeval: Archeia Template Optimization

You are running an autonomous improvement loop. Your goal: make Archeia's
generated documentation more useful to coding agents by iteratively editing
templates, re-generating bundles, measuring the effect via evals, and keeping
only what helps.

Do not pause to ask the human once the loop has started.

---

## Setup

You are in the Archeia repo root. Before entering the loop:

```bash
# Verify environment
test -f AGENTS.md && test -d skills/ && test -d evals/ && echo "repo OK"
claude --version

# Verify Phase 3 bundles exist for canary repos
test -f evals/archeia-output/polar/bundle-manifest.json && echo "polar bundle OK"
test -f evals/archeia-output/mitmproxy/bundle-manifest.json && echo "mitmproxy bundle OK"

# Create working branch
git checkout -b autoeval
```

If bundles are missing, stop — Phase 3 must be completed first.

---

## Mutation Scope

You may ONLY edit these files:

**Tech-docs templates** (9 files in `skills/archeia-write-tech-docs/assets/templates/`):
Architecture.md, System.json, Containers.json, Components.json, DataFlow.json,
Entities.json, StateMachine.json, Standards.md, Guide.md

**Write-readmes inline template** — in `skills/archeia-write-readmes/SKILL.md`,
only the `### README Template` and `### Writing Style` sections. Nothing else
in that file.

**Write-agents-docs inline template** — in `skills/archeia-write-agents-docs/SKILL.md`,
only the `## Writing Rules` section. Nothing else in that file.

Everything else is off-limits: eval harness, task configs, judge rubrics,
SKILL.md workflow logic, operating rules, evidence principle, scripts,
references, protocol docs, and skills 1/2/6 (scan-repo, scan-git,
draw-diagrams).

---

## Canary Eval Set

8 tasks, L2 condition only, run with `--model haiku`:

```
polar-ask-complex-01
polar-plan-complex-01
polar-implement-moderate-01
polar-implement-simple-01
mitmproxy-ask-complex-01
mitmproxy-plan-complex-01
mitmproxy-implement-moderate-01
mitmproxy-implement-simple-01
```

To run one cell:

```bash
python3 evals/harness/runner.py \
  --repo-id <REPO> \
  --condition l2 \
  --task-config evals/config/tasks/<REPO>/<TASK_ID>.yaml \
  --trial 1 \
  --model haiku \
  --work-root /tmp/archeia-autoeval
```

From each result JSON, extract `judge.total_score`, `judge.dimension_scores`,
`judge.weaknesses`, `metrics.total_tokens`, and `metrics.tool_call_count`.

Compute `mean_score` (mean of 8 total_scores) and `mean_tokens` (mean of 8
total_tokens).

---

## Dual Ratchet

A change is kept only if BOTH hold:

- **Quality**: `new_mean_score >= baseline_mean_score - 1.0`
- **Efficiency**: `new_mean_tokens <= baseline_mean_tokens * 1.05`

---

## The Loop

### Iteration 0: Baseline

Run all 8 canary cells with unmodified templates. Record `baseline_mean_score`,
`baseline_mean_tokens`, and `safe_commit = HEAD`. Print a results table. Read
every judge output carefully — the weaknesses are your starting signal.

### Each subsequent iteration:

**1 — Analyze.** Read the judge weaknesses and dimension scores from the last
run. Find the pattern: which dimension is weakest on average? Which weaknesses
recur across tasks? Do ask/plan/implement tasks fail differently? Focus on
the weakest spot — that is where template changes have the most headroom.

**2 — Hypothesize.** State clearly:

- What is wrong (grounded in judge feedback)
- Which template file you will change
- What the change is
- Which dimension should improve

**3 — Mutate.** Read the target template. Make one small, targeted edit — add
a section, restructure for clarity, improve the exemplar data, sharpen
inference signals, or remove content that produces generic output. One
conceptual change per iteration. Never remove the evidence-grounding
requirement or required sections. Keep structural metadata intact.

**4 — Regenerate bundles.** Re-run skills 3–5 on both canary repos to produce
updated `evals/archeia-output/` bundles reflecting your template change.

For each of `polar` and `mitmproxy`:

```bash
# Prepare worktree at pinned commit
python3 evals/scripts/prepare_phase3_workspace.py \
  --repo-id <REPO> \
  --work-root /tmp/archeia-autoeval-regen \
  --force
```

Then start a subagent rooted at the worktree. Give it this prompt followed by
the full contents of `.archeia-eval/subagent-packet.md` from the worktree:

> Run the Archeia pipeline in this repository. Do not use installed skills.
> Follow the attached packet exactly in order. Stop after all steps complete
> and summarize generated files, skipped outputs, and evidence gaps.

After the subagent finishes, capture the bundle:

```bash
python3 evals/scripts/capture_phase3_bundle.py \
  --repo-id <REPO> \
  --worktree /tmp/archeia-autoeval-regen/<REPO> \
  --force \
  --allow-invalid-evidence \
  --cleanup
```

**5 — Evaluate.** Run all 8 canary cells. Compute `new_mean_score` and
`new_mean_tokens`. Print a comparison table showing per-task deltas.

**6 — Ratchet.**

Both ratchets pass:
```bash
git add skills/
git commit -m "autoeval: <hypothesis summary> (score: X → Y, tokens: A → B)"
```
Update baselines and `safe_commit`.

Either ratchet fails:
```bash
git checkout <safe_commit> -- skills/
```

Three consecutive failures: stop iterating. Re-read all judge outputs from
the last successful baseline. Reconsider whether you are targeting the right
dimension or whether the weakness is addressable through template changes.
Then resume.

**7 — Log.** Record the iteration: hypothesis, target file, change summary,
score delta, token delta, which ratchets passed/failed, outcome
(committed hash or reverted), and any notable shifts in judge feedback.

Return to step 1.

---

## Stopping

Stop the loop when any of these hold:

- 20 iterations completed → proceed to full validation
- 5 consecutive iterations with no improvement → diminishing returns
- Mean score exceeds 85 → strong plateau

---

## Full Validation

After the loop ends, validate that canary-set improvements generalize:

Run all 50 tasks across all 5 repos under L2 with the default model (not
haiku). Compare against the pre-autoeval baseline. Check for regressions
on repos and categories outside the canary set — especially arq (negative
control, expect minimal change). Print a report: per-repo, per-category,
per-dimension, and token efficiency.

---

## Rules

- Never fabricate eval results. Always run the actual pipeline.
- Evidence grounding is sacred. Templates must never instruct skills to
  generate claims without file path citations.
- One template change per iteration. No batch mutations.
- Always read the current template before editing it.
- Do not modify anything outside `skills/` during the loop.
