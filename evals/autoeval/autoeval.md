# Autoeval

Autonomous skill improvement through eval-driven hill-climbing.

This is my interpretation of Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) adapted for AI agent skills. Autoresearch applies hill-climbing with a git ratchet to ML training scripts — autoeval applies the same pattern to the prompts, templates, and workflows that define what an agent does. It is an idea file, designed to be copy pasted to your own LLM Agent (e.g. Claude Code, OpenAI Codex, OpenCode, or etc.). Its goal is to communicate the high level idea, but your agent will build out the specifics in collaboration with you.

### The problem

A lot of people are building genuinely useful agent skills right now. But most measure success empirically — it works, it feels right, ship it. Few have structured evals, and almost nobody is closing the loop: using eval signal to automatically improve the skill itself.

Eval judges already produce structured feedback — dimension scores, weakness descriptions, efficiency metrics. That's a gradient signal. Autoeval uses it: the agent reads its own eval results, hypothesizes what to change, edits the skill, re-evaluates, and keeps only what helps. You set up the eval, define the mutation scope, and let it run.

### Relation to autoresearch

Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) is the direct inspiration. The structural mapping:

- `train.py` → the skill definition
- `val_bpb` → judge scores + efficiency metrics
- `prepare.py` (immutable) → the eval harness (immutable)
- `program.md` (human guidance) → the autoeval prompt (human guidance)
- 5-minute training run → eval suite execution
- git commit/revert → git commit/revert

The main difference is cost. Autoresearch runs ~12 experiments per hour on a single GPU. Autoeval runs maybe 1 per hour because eval involves spawning agents, running tasks, and judging output. This makes hypothesis quality more important — you can't brute-force the search space, so each iteration needs to be well-targeted based on judge feedback.

### Architecture

Three layers:

**The skill** — the thing being optimized. A system prompt, a SKILL.md, templates, a workflow definition. The autoeval agent modifies this. Everything else is read-only.

**The eval** — a repeatable measurement. Tasks with known-good answers or clear acceptance criteria, scored by a judge. Must be deterministic enough to ratchet on. Fixed during the loop — the agent never touches it.

**The ratchet** — git commit/revert. Before each mutation, note the commit. After eval: improved → commit, regressed → revert. The skill only accumulates wins. The git log is the experiment record.

### The loop

**Baseline.** Run the eval with the current skill. Record scores and metrics.

**Analyze.** Read judge output — weaknesses, dimension breakdowns, per-task details. Find the pattern: which dimension is weakest? Which weaknesses recur?

**Hypothesize.** A specific, testable prediction naming a file, a section, and an expected outcome. Vague hypotheses produce vague changes.

**Mutate.** One small, targeted edit. One conceptual change per iteration — if you change two things and the score goes up, you don't know which helped.

**Evaluate.** Run the eval again. Compare.

**Ratchet.** Improved → commit, update baseline. Regressed → revert. Log either way.

**Repeat.**

### Eval signal quality

The loop is only as good as the eval signal feeding it.

**Multi-dimensional scores** tell the agent where to focus. "Convention fit is 11/25" is actionable. "Score: 62" is not.

**Natural-language weaknesses** are the richest signal. "Failed to identify the test runner configuration" maps directly to a skill edit. A bare number doesn't.

**Multiple task types** prevent overfitting. Span different categories — understanding, planning, implementation — so the skill improves broadly.

**Low variance** makes the ratchet reliable. If identical runs produce scores of 60 and 75, a 2-point improvement means nothing.

### Scope control

Define an explicit mutation scope — what the agent can change and what it can't.

Start narrow. Templates before workflow logic. Templates are high-leverage (small change propagates everywhere) and low-risk. Expand scope once template-level gains plateau.

One change per iteration for attribution. Five simultaneous changes and a 3-point improvement teaches you nothing.

Deny lists prevent gaming. If the agent can touch the eval harness, it will eventually discover the easiest path is making the eval easier.

### Cost management

**Cheaper model for iteration.** Use a smaller model as proxy during the loop — if better instructions help a weaker model, they help a stronger one. Validate on the target model at gates.

**Canary subset.** 6-10 representative tasks, not the full suite. Full runs at validation gates only.

**Dual ratchet.** Track quality (scores) and efficiency (tokens, tool calls) independently. A change is kept only if neither regresses. Prevents trading quality for efficiency or vice versa.

### When this works / doesn't

Works when: eval signal is multi-dimensional, the skill has template-like structure where changes propagate predictably, evals are stable enough to ratchet on, there's room to improve.

Doesn't work when: eval is too noisy, skill is already near-optimal, the bottleneck is outside the mutation scope, or the judge only produces pass/fail without actionable feedback.

### Note

This is intentionally abstract. The exact skill format, eval harness, judge rubric, ratchet thresholds, and mutation scope depend on your domain. Share this with your LLM agent and work together to instantiate it. The document's only job is to communicate the pattern.
