from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.common import command_template_from_string, fill_command_template, load_data_file, run_command, utc_now


DEFAULT_JUDGE_COMMAND = ["claude", "--output-format", "json", "-p", "{prompt}"]


def rubric_for_category(category: str) -> str:
    if category.startswith("ask"):
        return (
            "1. Correctness: factual accuracy against ground truth.\n"
            "2. Completeness: covers all relevant systems and caveats.\n"
            "3. Evidence alignment: cites or reflects the repo-grounded flow.\n"
            "4. Communication quality: organized, concise, and directly useful."
        )
    if category.startswith("plan"):
        return (
            "1. Correctness: technically sound approach.\n"
            "2. Completeness: affected modules, sequencing, and risks covered.\n"
            "3. Convention fit: follows the repo's apparent patterns.\n"
            "4. Actionability: specific enough to implement."
        )
    return (
        "1. Correctness: change solves the task.\n"
        "2. Completeness: includes all required code-path updates.\n"
        "3. Convention fit: matches project structure and patterns.\n"
        "4. Verification: test/lint outcomes support the change."
    )


def build_judge_prompt(task: dict[str, Any], run_payload: dict[str, Any]) -> str:
    category = task.get("category", "implement")
    response_text = run_payload.get("agent_run", {}).get("stdout", "")
    diff_text = run_payload.get("diff", "")
    metrics = run_payload.get("metrics", {})
    code_quality = run_payload.get("code_quality", {})

    prompt = f"""
You are judging an Archeia evaluation run.

Task category: {category}
Task id: {task.get('id')}

Task prompt:
{task.get('prompt', '')}

Ground truth / reference:
{task.get('ground_truth', '')}

Acceptance criteria:
{json.dumps(task.get('acceptance_criteria', []), indent=2)}

Agent response:
{response_text}

Git diff:
{diff_text}

Code-quality signals:
{json.dumps(code_quality, indent=2, sort_keys=True)}

Efficiency signals:
{json.dumps(metrics, indent=2, sort_keys=True)}

Score the run from 0-100 using four equally weighted 0-25 dimensions:
{rubric_for_category(category)}

Return JSON only with this schema:
{{
  "total_score": 0,
  "dimension_scores": {{
    "correctness": 0,
    "completeness": 0,
    "convention_fit": 0,
    "verification_or_communication": 0
  }},
  "summary": "short paragraph",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "confidence": "low|medium|high"
}}
""".strip()
    return prompt


def _extract_json(text: str) -> dict[str, Any] | None:
    """Try to parse JSON from text, handling markdown code fences."""
    stripped = text.strip()
    if not stripped:
        return None

    # Direct JSON parse
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", stripped, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Last resort: find first { ... } block
    brace_match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def parse_judge_response(stdout: str) -> dict[str, Any]:
    stripped = stdout.strip()
    if not stripped:
        return {"status": "failed", "reason": "Judge produced empty output"}

    # The claude CLI with --output-format json wraps the result in an envelope
    # with {"type": "result", "result": "..."} — extract the inner result first.
    envelope = _extract_json(stripped)
    if envelope is not None:
        inner = envelope.get("result")
        if isinstance(inner, str):
            parsed = _extract_json(inner)
            if parsed is not None:
                parsed.setdefault("status", "completed")
                return parsed
        # If the envelope itself has judge fields, use it directly
        if "total_score" in envelope:
            envelope.setdefault("status", "completed")
            return envelope

    # Fallback: try parsing the raw stdout directly
    parsed = _extract_json(stripped)
    if parsed is not None:
        parsed.setdefault("status", "completed")
        return parsed

    return {
        "status": "failed",
        "reason": "Unable to parse judge JSON",
        "raw_output": stripped,
    }


def judge_run(
    task: dict[str, Any],
    run_payload: dict[str, Any],
    timeout_seconds: int = 300,
    command_template: list[str] | None = None,
) -> dict[str, Any]:
    prompt = build_judge_prompt(task, run_payload)
    template = command_template or DEFAULT_JUDGE_COMMAND
    command = fill_command_template(template, {"prompt": prompt})

    if shutil.which(command[0]) is None:
        return {
            "status": "skipped",
            "reason": f"Judge command not found: {command[0]}",
            "command": command,
            "prompt": prompt,
            "started_at": utc_now(),
            "finished_at": utc_now(),
        }

    result = run_command(command, cwd=Path.cwd(), timeout=timeout_seconds)
    payload = parse_judge_response(result["stdout"])
    payload["command"] = command
    payload["started_at"] = result["started_at"]
    payload["finished_at"] = result["finished_at"]
    if payload.get("status") == "failed":
        payload["stderr"] = result["stderr"]
        payload["prompt"] = prompt
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Judge an Archeia eval run")
    parser.add_argument("--task", required=True)
    parser.add_argument("--run-payload", required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--command-json")
    args = parser.parse_args()

    task = load_data_file(Path(args.task))
    run_payload = json.loads(Path(args.run_payload).read_text(encoding="utf-8"))
    payload = judge_run(
        task=task,
        run_payload=run_payload,
        timeout_seconds=args.timeout,
        command_template=command_template_from_string(args.command_json),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
