#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.phase3 import capture_phase3_bundle, cleanup_phase3_workspace


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture canonical Archeia outputs from a Phase 3 worktree")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--repos-path", default="evals/config/repos.yaml")
    parser.add_argument("--bundles-root", default="evals/config/bundles")
    parser.add_argument("--bundle-root")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-invalid-evidence", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    payload = capture_phase3_bundle(
        repo_id=args.repo_id,
        worktree=Path(args.worktree),
        repos_path=Path(args.repos_path),
        bundles_root=Path(args.bundles_root),
        bundle_root=Path(args.bundle_root) if args.bundle_root else None,
        force=args.force,
        allow_invalid_evidence=args.allow_invalid_evidence,
    )
    if args.cleanup:
        payload["cleanup"] = cleanup_phase3_workspace(
            repo_id=args.repo_id,
            worktree=Path(args.worktree),
            repos_path=Path(args.repos_path),
        )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
