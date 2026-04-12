from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
EVALS_ROOT = Path(__file__).resolve().parent


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: Any) -> Path:
    ensure_directory(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_data_file(path: str | Path) -> Any:
    data_path = Path(path)
    text = data_path.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        return yaml.safe_load(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{data_path} must be JSON-compatible YAML when PyYAML is unavailable"
        ) from exc


def copy_tree_contents(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    ensure_directory(destination)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            ensure_directory(target.parent)
            shutil.copy2(item, target)


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def run_command(command: list[str], cwd: Path, timeout: int, env: dict[str, str] | None = None) -> dict[str, Any]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    started_at = utc_now()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=merged_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        finished_at = utc_now()
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": -1,
            "stdout": (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            "stderr": (exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or ""),
            "started_at": started_at,
            "finished_at": finished_at,
            "timed_out": True,
            "timeout_seconds": timeout,
        }
    finished_at = utc_now()

    return {
        "command": command,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "started_at": started_at,
        "finished_at": finished_at,
    }


def command_template_from_string(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    payload = json.loads(raw)
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("Command template must be a JSON array of strings")
    return payload


def fill_command_template(template: list[str], substitutions: dict[str, str]) -> list[str]:
    rendered: list[str] = []
    for part in template:
        rendered.append(part.format(**substitutions))
    return rendered


def metric_value(payload: dict[str, Any], path: str, default: float | None = None) -> float | None:
    current: Any = payload
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return default
        current = current[segment]
    if isinstance(current, (int, float)):
        return float(current)
    return default


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def sample_stddev(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    average = mean(values)
    if average is None:
        return None
    variance = sum((value - average) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)


def confidence_interval_95(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    average = mean(values)
    if average is None:
        return None
    if len(values) == 1:
        return {"mean": average, "lower": average, "upper": average}
    deviation = sample_stddev(values)
    if deviation is None:
        return {"mean": average, "lower": average, "upper": average}
    margin = 1.96 * deviation / math.sqrt(len(values))
    return {"mean": average, "lower": average - margin, "upper": average + margin}
