from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.common import run_command


def parse_command(command: str | list[str] | None) -> list[str] | None:
    if command is None:
        return None
    if isinstance(command, list):
        return command
    return shlex.split(command)


def finding_count(command_result: dict[str, Any] | None) -> int | None:
    if command_result is None:
        return None
    output = f"{command_result.get('stdout', '')}\n{command_result.get('stderr', '')}".strip()
    if not output:
        return 0
    return len([line for line in output.splitlines() if line.strip()])


def run_optional_command(worktree: Path, command: str | list[str] | None, timeout_seconds: int) -> dict[str, Any] | None:
    parsed = parse_command(command)
    if not parsed:
        return None
    return run_command(parsed, cwd=worktree, timeout=timeout_seconds)


def run_code_quality_checks(
    worktree: Path,
    test_command: str | list[str] | None,
    lint_command: str | list[str] | None,
    timeout_seconds: int,
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tests = run_optional_command(worktree, test_command, timeout_seconds)
    lint = run_optional_command(worktree, lint_command, timeout_seconds)

    baseline_findings = finding_count(baseline)
    current_findings = finding_count(lint)
    lint_delta = None
    if baseline_findings is not None and current_findings is not None:
        lint_delta = current_findings - baseline_findings

    return {
        "tests": tests,
        "lint": lint,
        "lint_baseline": baseline,
        "lint_baseline_findings": baseline_findings,
        "lint_findings": current_findings,
        "lint_delta": lint_delta,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run optional tests/lint checks for an eval worktree")
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--test-command")
    parser.add_argument("--lint-command")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    payload = run_code_quality_checks(
        worktree=Path(args.worktree),
        test_command=args.test_command,
        lint_command=args.lint_command,
        timeout_seconds=args.timeout,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
