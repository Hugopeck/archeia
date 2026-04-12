from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))


EXPLORATION_TOOLS = {"read", "grep", "glob"}
ACTION_TOOLS = {"write", "edit", "multiedit", "apply_patch", "applypatch"}


def load_transcript(path: Path) -> Any:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        lines = [json.loads(line) for line in text.splitlines() if line.strip()]
        return lines


def walk_dicts(node: Any) -> Iterable[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk_dicts(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk_dicts(item)


def parse_timestamp(raw: Any) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(raw)
    if isinstance(raw, str):
        normalized = raw.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None
    return None


def normalize_tool_name(event: dict[str, Any]) -> str | None:
    for key in ("tool_name", "tool", "name"):
        value = event.get(key)
        if isinstance(value, str):
            lowered = value.strip().lower().replace("-", "_")
            if lowered in EXPLORATION_TOOLS or lowered in ACTION_TOOLS or event.get("type") in {"tool_use", "tool_call"}:
                return lowered
    return None


def collect_token_metrics(dicts: list[dict[str, Any]]) -> dict[str, int]:
    total_candidates: list[int] = []
    input_candidates: list[int] = []
    output_candidates: list[int] = []

    for event in dicts:
        for key in ("total_tokens",):
            value = event.get(key)
            if isinstance(value, int):
                total_candidates.append(value)
        usage = event.get("usage")
        if isinstance(usage, dict):
            if isinstance(usage.get("total_tokens"), int):
                total_candidates.append(usage["total_tokens"])
            if isinstance(usage.get("input_tokens"), int):
                input_candidates.append(usage["input_tokens"])
            if isinstance(usage.get("output_tokens"), int):
                output_candidates.append(usage["output_tokens"])
        for key in ("input_tokens", "prompt_tokens"):
            value = event.get(key)
            if isinstance(value, int):
                input_candidates.append(value)
        for key in ("output_tokens", "completion_tokens"):
            value = event.get(key)
            if isinstance(value, int):
                output_candidates.append(value)

    input_total = max(input_candidates) if input_candidates else 0
    output_total = max(output_candidates) if output_candidates else 0
    total = max(total_candidates) if total_candidates else input_total + output_total
    return {
        "input_tokens": input_total,
        "output_tokens": output_total,
        "total_tokens": total,
    }


def collect_metrics(transcript_path: Path) -> dict[str, Any]:
    payload = load_transcript(transcript_path)
    dicts = list(walk_dicts(payload))

    timestamps: list[datetime] = []
    tool_counts: dict[str, int] = {}
    first_action_timestamp: datetime | None = None

    for event in dicts:
        tool_name = normalize_tool_name(event)
        if tool_name:
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

        for key in ("timestamp", "created_at", "started_at", "finished_at", "time"):
            parsed = parse_timestamp(event.get(key))
            if parsed is not None:
                timestamps.append(parsed)
                if tool_name in ACTION_TOOLS and first_action_timestamp is None:
                    first_action_timestamp = parsed

    timestamps.sort()
    started_at = timestamps[0] if timestamps else None
    finished_at = timestamps[-1] if timestamps else None

    exploration_calls = sum(count for name, count in tool_counts.items() if name in EXPLORATION_TOOLS)
    action_calls = sum(count for name, count in tool_counts.items() if name in ACTION_TOOLS)
    ratio = None
    if action_calls:
        ratio = exploration_calls / action_calls

    token_metrics = collect_token_metrics(dicts)

    return {
        **token_metrics,
        "tool_counts": tool_counts,
        "tool_call_count": sum(tool_counts.values()),
        "exploration_calls": exploration_calls,
        "action_calls": action_calls,
        "exploration_to_action_ratio": ratio,
        "started_at": started_at.isoformat() if started_at else None,
        "finished_at": finished_at.isoformat() if finished_at else None,
        "time_to_completion_seconds": (finished_at - started_at).total_seconds() if started_at and finished_at else None,
        "time_to_first_edit_seconds": (first_action_timestamp - started_at).total_seconds()
        if started_at and first_action_timestamp
        else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect transcript metrics from a conversation log")
    parser.add_argument("transcript")
    args = parser.parse_args()
    print(json.dumps(collect_metrics(Path(args.transcript)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
