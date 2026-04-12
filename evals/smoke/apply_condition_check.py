"""Exercise apply_condition on the real arq bundle against a scratch worktree.

No agent invocation, no writes to evals/results/. The worktree is a fresh
git clone of the arq source repo placed under a caller-provided scratch
directory. On success, asserts the expected .archeia/codebase/** layout
landed. Exits 0 on pass, 1 on fail; writes a JSON summary to --summary.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Allow running as a standalone script from the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.common import load_data_file  # noqa: E402
from evals.harness.condition_applier import apply_condition  # noqa: E402


REQUIRED_PATHS_L1 = [
    # Root docs
    "AGENTS.md",
    "CLAUDE.md",
    # codebase/architecture
    ".archeia/codebase/architecture/architecture.md",
    ".archeia/codebase/architecture/system.json",
    ".archeia/codebase/architecture/containers.json",
    ".archeia/codebase/architecture/components.json",
    ".archeia/codebase/architecture/dataflow.json",
    # codebase/standards
    ".archeia/codebase/standards/standards.md",
    # codebase/guide
    ".archeia/codebase/guide.md",
    # codebase/diagrams
    ".archeia/codebase/diagrams/context.md",
    ".archeia/codebase/diagrams/containers.md",
    ".archeia/codebase/diagrams/sequence-primary.md",
]

# Paths that MUST NOT exist after the new layout migration — if any of
# these are present, we know the bundle rename leaked.
FORBIDDEN_PATHS = [
    ".archeia/Architecture.md",
    ".archeia/System.json",
    ".archeia/Containers.json",
    ".archeia/Components.json",
    ".archeia/DataFlow.json",
    ".archeia/Standards.md",
    ".archeia/Guide.md",
    ".archeia/diagrams",  # directory; listdir check below
]


def git_clone_worktree(source: Path, commit: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--no-local", "--quiet", str(source), str(destination)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(destination), "checkout", "--quiet", commit],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="arq")
    parser.add_argument("--condition", default="l1")
    parser.add_argument("--scratch", required=True, help="Scratch root for the worktree")
    parser.add_argument("--summary", required=True, help="Path to write summary JSON")
    args = parser.parse_args()

    repos = load_data_file(REPO_ROOT / "evals" / "config" / "repos.yaml")
    repo = next((r for r in repos["repos"] if r["id"] == args.repo_id), None)
    if repo is None:
        print(f"smoke: repo {args.repo_id!r} not in repos.yaml", file=sys.stderr)
        return 1

    source = Path(repo["source_path"])
    bundle = REPO_ROOT / repo["archeia_output_path"]
    if not source.is_dir():
        print(f"smoke: source clone missing at {source}", file=sys.stderr)
        return 1
    if not bundle.is_dir():
        print(f"smoke: bundle missing at {bundle}", file=sys.stderr)
        return 1

    scratch = Path(args.scratch)
    worktree = scratch / f"{args.repo_id}-{args.condition}"
    print(f"smoke: cloning {source} -> {worktree} @ {repo['commit'][:10]}")
    git_clone_worktree(source, repo["commit"], worktree)

    summary: dict = {
        "repo_id": args.repo_id,
        "condition": args.condition,
        "worktree": str(worktree),
        "bundle": str(bundle),
    }

    print("smoke: applying condition")
    condition_summary = apply_condition(
        repo_id=args.repo_id,
        condition_id=args.condition,
        worktree=worktree,
        archeia_output=bundle,
        conditions_path=REPO_ROOT / "evals" / "config" / "conditions.yaml",
    )
    summary["condition_application"] = condition_summary

    # Check required files exist
    missing = [p for p in REQUIRED_PATHS_L1 if not (worktree / p).exists()]
    summary["missing_required"] = missing

    # Check forbidden (old-layout) files do NOT exist
    leaked = []
    for p in FORBIDDEN_PATHS:
        target = worktree / p
        if target.exists():
            leaked.append(p)
    summary["leaked_old_paths"] = leaked

    ok = not missing and not leaked
    summary["status"] = "pass" if ok else "fail"

    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if ok:
        print("smoke: PASS — expected .archeia/codebase/** layout present, no old paths leaked")
        return 0

    print("smoke: FAIL", file=sys.stderr)
    if missing:
        print(f"  missing required paths ({len(missing)}):", file=sys.stderr)
        for p in missing:
            print(f"    - {p}", file=sys.stderr)
    if leaked:
        print(f"  leaked old-layout paths ({len(leaked)}):", file=sys.stderr)
        for p in leaked:
            print(f"    - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
