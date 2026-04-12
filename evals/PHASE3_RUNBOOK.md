# Phase 3 Runbook

This runbook is for the orchestrator agent responsible for producing canonical
Archeia output bundles under `evals/archeia-output/<repo-id>/`.

The Phase 3 workflow does **not** rely on installed Archeia slash commands.
Instead, it copies the exact contents of each `skills/<name>/SKILL.md` into a
single packet and passes the packet path to a subagent running in the pinned
repo worktree.

All commands run from the Archeia repo root:
`/Users/hugopeck/conductor/workspaces/archeia/athens`

Helper scripts referenced by the pipeline (pass these paths to subagents):
- `discover.sh`: `skills/archeia-write-tech-docs/scripts/discover.sh`
- `git-scanner.sh`: `skills/archeia-scan-git/scripts/git-scanner.sh`
- `validate-evidence.sh`: `skills/archeia-write-tech-docs/scripts/validate-evidence.sh`

## Inputs

- Repo registry: `evals/config/repos.yaml`
- Bundle spec: `evals/config/bundles/<repo-id>.yaml`
- Skill definitions: `skills/*/SKILL.md`

## Outputs

- Canonical bundle: `evals/archeia-output/<repo-id>/`
- Provenance manifest: `evals/archeia-output/<repo-id>/bundle-manifest.json`
- Colocated manifests:
  - `evals/archeia-output/<repo-id>/colocated-readmes/manifest.json`
  - `evals/archeia-output/<repo-id>/colocated-agents/manifest.json`

## Step 1: Prepare the pinned worktree

```bash
python3 evals/scripts/prepare_phase3_workspace.py --repo-id <repo-id> --work-root /tmp/archeia-phase3 --force
```

This does three things:

1. Creates a detached git worktree at the repo's pinned commit.
2. Writes `.archeia-eval/phase3-instructions.txt` inside the worktree.
3. Writes `.archeia-eval/subagent-packet.md`, which concatenates the ordered
   `SKILL.md` contents the subagent should follow.

The returned JSON includes:

- `worktree` — absolute path to the worktree (e.g. `/tmp/archeia-phase3/<repo-id>`)
- `packet_path` — absolute path to the packet file
- `instructions_path`
- `pipeline_order`

## Step 2: Launch the subagent

Use the Agent tool to launch a background subagent. Pass it the packet path
(not the packet contents — the packet is too large to inline). The subagent
must read and follow the packet from disk.

Use this wrapper prompt, substituting `<worktree>` with the absolute path from
Step 1:

```text
Run the Archeia Phase 3 pipeline in the repository at <worktree>.
Do not use installed skills.

Read the packet at <worktree>/.archeia-eval/subagent-packet.md and follow it
exactly in order, applying each embedded SKILL.md to this repo.

Your working directory is <worktree>. Use absolute paths for all file
operations. When bash commands reference helper scripts, find them at:
- discover.sh: /Users/hugopeck/conductor/workspaces/archeia/athens/skills/archeia-write-tech-docs/scripts/discover.sh
- git-scanner.sh: /Users/hugopeck/conductor/workspaces/archeia/athens/skills/archeia-scan-git/scripts/git-scanner.sh
- validate-evidence.sh: /Users/hugopeck/conductor/workspaces/archeia/athens/skills/archeia-write-tech-docs/scripts/validate-evidence.sh

Run all bash commands prefixed with: cd <worktree> &&

Stop after all six steps are complete and summarize generated files,
skipped attempted outputs, and evidence gaps.
```

The subagent generates outputs directly in the worktree:
- Root docs: `AGENTS.md`, `CLAUDE.md`
- System docs under `.archeia/`
- Colocated `README.md` files
- Colocated `agents.md` and `claude.md` files
- Mermaid diagrams under `.archeia/codebase/diagrams/`

## Step 3: Capture the canonical bundle

After the subagent completes, run from the Archeia repo root:

```bash
python3 evals/scripts/capture_phase3_bundle.py \
  --repo-id <repo-id> \
  --worktree /tmp/archeia-phase3/<repo-id> \
  --force \
  --cleanup
```

This script:

1. Verifies the worktree is still on the pinned commit.
2. Runs evidence validation.
3. Copies canonical root docs and `.archeia/` outputs into `evals/archeia-output/<repo-id>/`.
4. Detects generated colocated docs from git status.
5. Copies colocated docs into the bundle and writes explicit manifests.
6. Writes `bundle-manifest.json` with provenance and validation results.
7. Removes the temporary worktree (`--cleanup`).

If evidence validation reports invalid references and the bundle should be
inspected anyway, rerun with `--allow-invalid-evidence`.

## Invariants

- Do not treat `evals/archeia-output/` as hand-authored content.
- Do not copy `.archeia/codebase/scan-report.md` or `.archeia/codebase/git-report.md` into the final bundle.
- Do not mirror the whole repo into the bundle.
- Do preserve colocated doc paths through explicit manifests.
- Do keep the skill order exactly as declared in the bundle spec.
