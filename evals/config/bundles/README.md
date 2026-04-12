# Bundle Specs

Files in this directory are **Phase 2 preparation artifacts**. They do not
contain generated documentation; they define how Phase 3 should run the real
Archeia skill pipeline and capture canonical outputs into
`evals/archeia-output/<repo-id>/`.

Each repo spec must include:

- `repo_id`
- `source_path`
- `commit`
- `pipeline_order`
- `required_outputs`
- `always_attempted_outputs`
- `conditional_expectations`
- `copy_rules`
- `validation`
- `notes`

### Expectation values

Use these values for conditional outputs:

- `expected_present` — this output is likely expected if evidence behaves as anticipated
- `expected_skip` — this output is normally expected to be absent due to insufficient evidence
- `evidence_dependent` — the repo may or may not produce the output depending on what the skill finds

### Phase 3 capture rules

During Phase 3, the operator-run skill pipeline should:

1. Run the six skills in the declared order against a temporary repo workspace.
2. Copy only canonical root docs, `.archeia/` outputs, diagrams, and generated
   colocated docs into `evals/archeia-output/<repo-id>/`.
3. Exclude `.archeia/codebase/scan-report.md` and `.archeia/codebase/git-report.md` from the final
   bundle.
4. Generate explicit `manifest.json` files for both colocated bundles.
5. Write `bundle-manifest.json` with provenance and evidence-validation results.

Recommended operator workflow:

```bash
python3 evals/scripts/prepare_phase3_workspace.py --repo-id <repo-id> --work-root /tmp/archeia-phase3
# start a subagent in the generated worktree and paste .archeia-eval/subagent-packet.md
python3 evals/scripts/capture_phase3_bundle.py --repo-id <repo-id> --worktree /tmp/archeia-phase3/<repo-id> --force
```

The detailed packet-based runbook lives at `evals/PHASE3_RUNBOOK.md`.
