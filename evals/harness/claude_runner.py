from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.common import command_template_from_string, fill_command_template, run_command, utc_now


EVAL_SYSTEM_PROMPT = (
    "CRITICAL RULE: You MUST use your tools to read files in this repository before answering. "
    "Do NOT answer from memory or training data. "
    "Start by exploring the project structure with Bash(ls) or Glob, then read the specific files "
    "needed to answer the question. "
    "Every claim you make must cite a specific file path you actually read in this session. "
    "If you answer without reading files first, your response will be scored as zero."
)

DEFAULT_AGENT_COMMAND = [
    "claude",
    "--model", "sonnet",
    "--output-format", "stream-json",
    "--verbose",
    "--permission-mode", "auto",
    "--append-system-prompt", EVAL_SYSTEM_PROMPT,
    "-p", "{prompt}",
]


def run_agent(
    prompt: str,
    worktree: Path,
    transcript_path: Path,
    timeout_seconds: int = 900,
    command_template: list[str] | None = None,
) -> dict[str, Any]:
    template = command_template or DEFAULT_AGENT_COMMAND
    substitutions = {
      "prompt": prompt,
      "cwd": str(worktree),
      "transcript": str(transcript_path),
    }
    command = fill_command_template(template, substitutions)

    if shutil.which(command[0]) is None:
        return {
            "status": "skipped",
            "reason": f"Agent command not found: {command[0]}",
            "command": command,
            "transcript_path": str(transcript_path),
            "started_at": utc_now(),
            "finished_at": utc_now(),
        }

    result = run_command(command, cwd=worktree, timeout=timeout_seconds)
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    if not transcript_path.exists():
        transcript_path.write_text(result["stdout"], encoding="utf-8")

    # Extract the final result text from stream-json output.
    # The stream contains JSONL; the last line with type=result has the agent's answer.
    agent_result_text = result["stdout"]
    for line in reversed(result["stdout"].splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get("type") == "result":
                agent_result_text = obj.get("result", result["stdout"])
                break
        except (json.JSONDecodeError, TypeError):
            continue

    return {
        "status": "completed" if result["exit_code"] == 0 else "failed",
        "command": command,
        "exit_code": result["exit_code"],
        "stdout": agent_result_text,
        "stderr": result["stderr"],
        "transcript_path": str(transcript_path),
        "started_at": result["started_at"],
        "finished_at": result["finished_at"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the configured agent CLI for one evaluation prompt")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--command-json")
    args = parser.parse_args()

    result = run_agent(
        prompt=args.prompt,
        worktree=Path(args.worktree),
        transcript_path=Path(args.transcript),
        timeout_seconds=args.timeout,
        command_template=command_template_from_string(args.command_json),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
