from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.collectors.code_quality import run_code_quality_checks
from evals.collectors.metrics import collect_metrics
from evals.common import (
    EVALS_ROOT,
    command_template_from_string,
    ensure_directory,
    load_data_file,
    run_command,
    utc_now,
    write_json,
)
from evals.harness.claude_runner import DEFAULT_AGENT_COMMAND, run_agent
from evals.harness.condition_applier import apply_condition
from evals.judges.llm_judge import judge_run


def repo_map(repos_path: Path) -> dict[str, Any]:
    payload = load_data_file(repos_path)
    return {item["id"]: item for item in payload.get("repos", [])}


def git_env() -> dict[str, str]:
    return {
        "GIT_AUTHOR_NAME": "Archeia Eval",
        "GIT_AUTHOR_EMAIL": "archeia-eval@example.com",
        "GIT_COMMITTER_NAME": "Archeia Eval",
        "GIT_COMMITTER_EMAIL": "archeia-eval@example.com",
    }


def create_worktree(source_repo: Path, commit: str, destination: Path, retries: int = 5) -> None:
    # Prune stale worktree references before creating a new one.
    subprocess.run(
        ["git", "-C", str(source_repo), "worktree", "prune"],
        check=False,
        capture_output=True,
        text=True,
    )
    ensure_directory(destination.parent)
    # If the destination already exists (stale from a prior failed run), remove it.
    if destination.exists():
        subprocess.run(
            ["git", "-C", str(source_repo), "worktree", "remove", "--force", str(destination)],
            check=False,
            capture_output=True,
            text=True,
        )
    # Retry with jittered backoff to handle concurrent git lock contention.
    for attempt in range(retries):
        result = subprocess.run(
            ["git", "-C", str(source_repo), "worktree", "add", "--detach", str(destination), commit],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return
        if attempt < retries - 1:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
            # Re-prune before retry in case a concurrent agent finished cleanup.
            subprocess.run(
                ["git", "-C", str(source_repo), "worktree", "prune"],
                check=False,
                capture_output=True,
                text=True,
            )
    # Final attempt failed — raise with stderr context.
    raise subprocess.CalledProcessError(
        result.returncode,
        result.args,
        output=result.stdout,
        stderr=result.stderr,
    )


def remove_worktree(source_repo: Path, destination: Path) -> None:
    subprocess.run(
        ["git", "-C", str(source_repo), "worktree", "remove", "--force", str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    if destination.exists():
        shutil.rmtree(destination, ignore_errors=True)


def commit_condition_state(worktree: Path) -> dict[str, Any]:
    run_command(["git", "add", "-A"], cwd=worktree, timeout=60, env=git_env())
    commit = run_command(
        ["git", "commit", "-m", "Apply evaluation condition"],
        cwd=worktree,
        timeout=60,
        env=git_env(),
    )
    return commit


def current_diff(worktree: Path) -> str:
    diff = run_command(["git", "diff", "--no-ext-diff"], cwd=worktree, timeout=120)
    return diff["stdout"]


def result_path(results_root: Path, repo_id: str, task_id: str, condition_id: str, trial: int) -> Path:
    return results_root / repo_id / task_id / condition_id / f"trial-{trial}.json"


def orchestrate_run(args: argparse.Namespace) -> dict[str, Any]:
    repos = repo_map(Path(args.repos_path))
    if args.repo_id not in repos:
        raise KeyError(f"Unknown repo: {args.repo_id}")

    repo = repos[args.repo_id]
    task = load_data_file(Path(args.task_config))
    task_repo_id = task.get("repo_id")
    if task_repo_id and task_repo_id != args.repo_id:
        raise ValueError(f"Task repo_id {task_repo_id!r} does not match --repo-id {args.repo_id!r}")
    task_id = task.get("id", Path(args.task_config).stem)
    work_root = Path(args.work_root) if args.work_root else Path(tempfile.mkdtemp(prefix="archeia-eval-"))
    worktree = work_root / f"{args.repo_id}-{args.condition}-{task_id}-trial{args.trial}"
    transcript_path = worktree / ".archeia-eval" / "conversation.json"
    results_root = Path(args.results_root)

    payload: dict[str, Any] = {
        "started_at": utc_now(),
        "repo_id": args.repo_id,
        "condition_id": args.condition,
        "trial": args.trial,
        "task": task,
        "repo": repo,
        "status": "initialized",
    }

    if args.dry_run:
        payload.update(
            {
                "status": "dry_run",
                "work_root": str(work_root),
                "worktree": str(worktree),
                "transcript_path": str(transcript_path),
                "result_path": str(result_path(results_root, args.repo_id, task_id, args.condition, args.trial)),
            }
        )
        return payload

    source_repo = Path(repo["source_path"])
    archeia_output = Path(repo["archeia_output_path"])
    create_worktree(source_repo, repo["commit"], worktree)

    output_path = result_path(results_root, args.repo_id, task_id, args.condition, args.trial)
    try:
        payload["condition_application"] = apply_condition(
            repo_id=args.repo_id,
            condition_id=args.condition,
            worktree=worktree,
            archeia_output=archeia_output,
            conditions_path=Path(args.conditions_path),
        )
        payload["condition_commit"] = commit_condition_state(worktree)

        baseline_commands = repo.get("commands", {})
        lint_before = run_code_quality_checks(
            worktree=worktree,
            test_command=None,
            lint_command=baseline_commands.get("lint"),
            timeout_seconds=args.quality_timeout,
        )

        agent_template = command_template_from_string(args.agent_command_json)
        if agent_template is None and args.model:
            agent_template = list(DEFAULT_AGENT_COMMAND)
            model_idx = agent_template.index("--model") + 1
            agent_template[model_idx] = args.model

        payload["agent_run"] = run_agent(
            prompt=task["prompt"],
            worktree=worktree,
            transcript_path=transcript_path,
            timeout_seconds=args.agent_timeout,
            command_template=agent_template,
        )
        payload["metrics"] = collect_metrics(transcript_path)
        payload["diff"] = current_diff(worktree)

        test_command = task.get("commands", {}).get("test") or baseline_commands.get("test")
        lint_command = task.get("commands", {}).get("lint") or baseline_commands.get("lint")
        payload["code_quality"] = run_code_quality_checks(
            worktree=worktree,
            test_command=test_command,
            lint_command=lint_command,
            timeout_seconds=args.quality_timeout,
            baseline=lint_before.get("lint"),
        )

        if args.skip_judge:
            payload["judge"] = {"status": "skipped", "reason": "--skip-judge"}
        else:
            payload["judge"] = judge_run(
                task=task,
                run_payload=payload,
                timeout_seconds=args.judge_timeout,
                command_template=command_template_from_string(args.judge_command_json),
            )

        payload["status"] = "completed"
    except Exception as exc:
        payload["status"] = "failed"
        payload["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        payload["finished_at"] = utc_now()
        payload["result_path"] = str(output_path)
        write_json(output_path, payload)
        if args.keep_worktree:
            payload["kept_worktree"] = str(worktree)
        else:
            remove_worktree(source_repo, worktree)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single Archeia evaluation trial")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--task-config", required=True)
    parser.add_argument("--trial", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--keep-worktree", action="store_true")
    parser.add_argument("--work-root")
    parser.add_argument("--repos-path", default=str(EVALS_ROOT / "config" / "repos.yaml"))
    parser.add_argument("--conditions-path", default=str(EVALS_ROOT / "config" / "conditions.yaml"))
    parser.add_argument("--results-root", default=str(EVALS_ROOT / "results" / "raw"))
    parser.add_argument("--agent-timeout", type=int, default=900)
    parser.add_argument("--judge-timeout", type=int, default=300)
    parser.add_argument("--quality-timeout", type=int, default=600)
    parser.add_argument("--model", default=None, help="Override the agent model (e.g. sonnet, opus)")
    parser.add_argument("--agent-command-json")
    parser.add_argument("--judge-command-json")
    args = parser.parse_args()

    payload = orchestrate_run(args)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
