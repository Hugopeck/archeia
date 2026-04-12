# Autoeval for Archeia

Autonomous skill improvement through eval-driven iteration.

## Goal

Archeia generates documentation to help AI agents navigate codebases. The eval
framework measures whether that documentation actually works — does it help
agents complete tasks faster and better? But until now, the signal from evals
has been read by humans and applied manually.

Autoeval closes the loop. An AI agent reads eval judge feedback, forms
hypotheses about what to improve in the documentation templates, makes a
change, re-runs evals, and keeps only what helps. The result: templates that
produce documentation optimized for agent consumption, discovered through
systematic experimentation rather than intuition.

## Philosophy

This is adapted from [Karpathy's autoresearch](https://github.com/karpathy/autoresearch),
which uses the same hill-climbing pattern for ML training scripts:

| Concept | Autoresearch (Karpathy) | Autoeval (Archeia) |
|---------|------------------------|----------------------|
| What gets modified | `train.py` | Template files in `skills/` |
| What gets measured | `val_bpb` (single metric) | `judge.total_score` + `total_tokens` (dual ratchet) |
| Evaluation cost | 5 minutes | ~1-2 hours |
| Ratchet mechanism | git commit/revert | git commit/revert |
| Search strategy | Hill climbing, one change at a time | Hill climbing, one change at a time |
| Signal source | Loss curve | Judge weaknesses + dimension scores |

The core insight is the same: you don't need sophisticated search when you have
a clear metric, a cheap-enough eval, and a ratchet that only accumulates wins.

## The Idea

The eval judge already tells us what's wrong. Each eval run produces:

- **Dimension scores** (correctness, completeness, convention_fit, verification)
  showing where the documentation helps and where it falls short
- **Weaknesses** — specific descriptions of what the agent struggled with
- **Token counts** — how much exploration the agent needed

These signals map directly to template changes. If agents consistently score
low on convention_fit, the Standards.md template might not be prompting for
enough detail about coding conventions. If token counts are high, the
Architecture.md template might not be surfacing the right structural
information upfront.

The autoeval agent reads these signals, forms a hypothesis, edits a
template, regenerates the documentation bundles, and measures whether the
change helped. Good changes accumulate. Bad changes disappear.

## How It Works

The agent reads `program.md` and executes this loop:

```
     ┌────────────────┐
     │  Run baseline   │ ← 8 eval tasks, record scores + tokens
     │  (iteration 0)  │
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │    Analyze      │ ← Read judge weaknesses, find patterns
     │    judge output │
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │   Hypothesize   │ ← "Standards.md doesn't prompt for test
     │                 │    patterns → low convention_fit scores"
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │    Mutate       │ ← Edit one template file
     │    template     │
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │   Regenerate    │ ← Re-run skills 3-5 on canary repos
     │    bundles      │    to produce updated documentation
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │    Evaluate     │ ← Run 8 eval tasks with updated docs
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │    Ratchet      │ ── PASS ──→ git commit, update baseline
     │  (dual check)   │
     └───────┬────────┘
             │ FAIL
             │
     ┌───────▼────────┐
     │    Revert       │ ← git checkout to restore templates
     └───────┬────────┘
             │
             └──────────→ Loop back to Analyze
```

The dual ratchet ensures changes are kept only when:
- Quality doesn't drop (mean judge score within 1 point of baseline)
- Efficiency doesn't regress (mean tokens within 5% of baseline)

## Decisions

**Why Haiku for loop iterations?**
Each iteration runs 8 eval cells. Using the target model (Opus/Sonnet) would
cost significantly more. Haiku is used as a proxy: if better documentation
helps a smaller model navigate a codebase, it helps a larger model too. The
full validation gate at the end uses the target model to confirm.

**Why 8 canary tasks, not all 50?**
50 tasks × ~10 min each = ~8 hours per iteration. 8 tasks ≈ 80 minutes. This
allows ~12 iterations overnight instead of ~3. The 8 tasks cover ask, plan,
and implement categories across both polar (529k LOC, complex) and mitmproxy
(160k LOC, medium). Implement tasks get 50% weight since that's where
documentation has the most direct impact on agent behavior.

**Why templates only (Phase 1)?**
Templates define what the generated documentation looks like — sections,
structure, exemplar data, inference signals. They're the highest-leverage
mutation target: a small change to a template propagates to every repo's
generated docs. SKILL.md workflow edits (Phase 2) are more powerful but
harder to evaluate — a workflow change might alter exploration strategy,
which has cascading effects that are harder to attribute.

**Why dual ratchet instead of a single composite score?**
A composite metric (e.g., 0.7 × quality + 0.3 × efficiency) hides tradeoffs.
The dual ratchet makes them explicit: you can see exactly which constraint a
failed change violated. It also prevents the optimizer from trading quality
for efficiency or vice versa — both must hold.

**Why these 3 skills?**
The 6 skills form a pipeline. Skills 1-2 (scan-repo, scan-git) produce
intermediate data that agents never read directly. Skill 6 (draw-diagrams)
produces Mermaid visualizations unlikely to move judge scores. Skills 3-5
produce the documents agents actually consume during eval tasks:
- write-tech-docs: Architecture.md, AGENTS.md, Standards.md, Guide.md, C4 JSONs
- write-readmes: colocated README.md per directory
- write-agents-docs: colocated agents.md per directory

**Why one change per iteration?**
Attribution. If you change two templates and the score improves, you don't
know which helped. Single changes make the ratchet meaningful and failures
informative.

## Assumptions

- **Relative improvements transfer across models.** A template change that
  helps Haiku should help Opus. The information content of the generated
  documentation is model-agnostic — clearer architecture docs reduce
  exploration regardless of the model reading them.

- **Judge scores are stable enough to ratchet on.** The 1-point tolerance
  on the quality ratchet accounts for noise, but assumes the LLM judge
  produces roughly consistent scores for the same input. If judge variance
  is high, the ratchet will be noisy and may reject real improvements.

- **Template changes are the highest-leverage mutation target.** Templates
  define output structure and content. If the skills' workflow logic
  (exploration strategy, file reading order, generation sequence) is the
  bottleneck, template changes alone won't move the needle.

- **The canary set is representative.** 8 tasks across 2 repos may not
  cover all failure modes. A template change that helps on ask-complex
  tasks might not help (or might hurt) implement-complex tasks that aren't
  in the canary set.

- **Phase 3 bundles are valid baselines.** The existing bundles in
  `evals/archeia-output/` were generated correctly and represent the
  current skill quality. If they were generated with bugs or incomplete
  exploration, the baseline is artificially low.

## Limitations

- **Expensive iterations.** Each loop iteration takes ~1-2 hours (bundle
  regeneration + 8 eval cells). At most ~12 iterations in a 24-hour run.
  This is much slower than Karpathy's ~12 iterations per hour.

- **Regeneration is the bottleneck.** Re-running skills 3-5 on two repos
  requires spawning subagents, which is slow and costs tokens. A future
  version could short-circuit this by editing bundles directly for fast
  hypothesis testing, then back-porting confirmed improvements to templates.

- **No multi-step hypothesis chaining.** Each iteration is independent.
  The agent can't plan a sequence of coordinated changes across templates
  — it must improve one template at a time and hope the gains compose.

- **Haiku proxy fidelity.** While relative improvements likely transfer,
  edge cases may not. A documentation pattern that helps Haiku might be
  irrelevant to a model that already has stronger reasoning.

- **Canary coverage.** 8 tasks may not expose all documentation failure
  modes. The full validation gate catches regressions but only after the
  loop completes.

- **Single trial per task.** No multi-trial averaging means results are
  noisy. A failed iteration might have succeeded on a re-roll. The 1-point
  tolerance partially addresses this.

## Future Improvements

- **Phase 2: SKILL.md workflow edits.** Unlock modifications to exploration
  strategy, file reading priorities, generation ordering, and self-validation
  logic.

- **Direct bundle editing.** Test documentation changes by editing
  `evals/archeia-output/` directly, bypassing the expensive regeneration
  step. Back-port confirmed improvements to templates. This could reduce
  iteration time from ~2 hours to ~15 minutes.

- **Multi-trial averaging.** Run each eval cell 2-3 times and average
  scores before ratcheting. Reduces noise at the cost of 2-3× longer
  iterations.

- **Adaptive canary selection.** After each iteration, swap the weakest
  canary task for a different one to broaden coverage over time.

- **Cross-condition delta tracking.** Run L0 and L1 alongside L2 to
  measure not just absolute quality but the improvement delta that Archeia
  provides over native docs.

- **Automated stopping criteria.** Track score trajectory and stop when
  the rate of improvement flattens, rather than using a fixed iteration
  count.

- **Hypothesis memory.** Maintain a searchable log of past hypotheses
  and outcomes so the agent doesn't re-try failed approaches.

- **Template A/B testing.** Run two template variants in parallel on
  different canary subsets to compare approaches without committing to
  either.

## File Structure

```
evals/autoeval/
├── README.md        ← You are here
└── program.md       ← The executable prompt for the agent loop
```

The experiment log is maintained by the agent during execution (in memory
or in a scratch file) and is not committed to the repo.

## Running It

Give an AI agent `program.md` as its prompt. The agent will:

1. Verify the environment and create a working branch
2. Run baseline evals (iteration 0)
3. Enter the autonomous improvement loop
4. Commit successful changes with descriptive messages
5. Stop after 20 iterations or when improvements plateau
6. Run full validation to confirm generalization

Review the git log on the `autoeval` branch to see what changed and why.
