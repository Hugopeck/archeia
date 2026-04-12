#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.phase3 import prepare_phase3_workspace


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a pinned temporary worktree for Phase 3 bundle generation")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--repos-path", default="evals/config/repos.yaml")
    parser.add_argument("--bundles-root", default="evals/config/bundles")
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--work-root")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    payload = prepare_phase3_workspace(
        repo_id=args.repo_id,
        repos_path=Path(args.repos_path),
        bundles_root=Path(args.bundles_root),
        skills_root=Path(args.skills_root),
        work_root=Path(args.work_root) if args.work_root else None,
        force=args.force,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
