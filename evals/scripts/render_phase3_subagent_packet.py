#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.phase3 import render_phase3_subagent_packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Phase 3 skill packet that should be pasted into a subagent")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--repos-path", default="evals/config/repos.yaml")
    parser.add_argument("--bundles-root", default="evals/config/bundles")
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--worktree")
    parser.add_argument("--output")
    parser.add_argument("--print-packet", action="store_true")
    args = parser.parse_args()

    payload = render_phase3_subagent_packet(
        repo_id=args.repo_id,
        repos_path=Path(args.repos_path),
        bundles_root=Path(args.bundles_root),
        skills_root=Path(args.skills_root),
        worktree=Path(args.worktree) if args.worktree else None,
        output_path=Path(args.output) if args.output else None,
    )

    if args.print_packet:
        print(payload["packet"])
    else:
        payload = dict(payload)
        payload.pop("packet", None)
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
