from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))

from evals.common import copy_tree_contents, ensure_directory, load_data_file, remove_path


def load_condition_map(conditions_path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    payload = load_data_file(conditions_path)
    doc_sets = payload.get("doc_sets", {})
    conditions = {item["id"]: item for item in payload.get("conditions", [])}
    return doc_sets, conditions


def resolve_colocated_entries(bundle_root: Path) -> list[dict[str, str]]:
    if not bundle_root.exists():
        return []

    manifest_path = bundle_root / "manifest.json"
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries: list[dict[str, str]] = []
        for item in payload:
            entries.append(
                {
                    "source": str(bundle_root / item["source"]),
                    "target": item["target"],
                }
            )
        return entries

    entries = []
    for file_path in sorted(path for path in bundle_root.rglob("*") if path.is_file()):
        if file_path.name == "manifest.json":
            continue
        entries.append(
            {
                "source": str(file_path),
                "target": str(file_path.relative_to(bundle_root)),
            }
        )
    return entries


def remove_generated_docs(worktree: Path, archeia_output: Path, doc_sets: dict[str, Any]) -> list[str]:
    removed: list[str] = []

    for relative_path in doc_sets.get("root_docs", []):
        target = worktree / relative_path
        if target.exists():
            remove_path(target)
            removed.append(relative_path)

    for relative_path in doc_sets.get("archeia", []):
        target = worktree / relative_path
        if target.exists():
            remove_path(target)
            removed.append(relative_path)

    for bundle_name in ("colocated-readmes", "colocated-agents"):
        for entry in resolve_colocated_entries(archeia_output / bundle_name):
            target = worktree / entry["target"]
            if target.exists():
                remove_path(target)
                removed.append(entry["target"])

    return sorted(set(removed))


def copy_entry(source: Path, destination: Path) -> None:
    ensure_directory(destination.parent)
    destination.write_bytes(source.read_bytes())


def apply_doc_set(worktree: Path, archeia_output: Path, doc_set: str, doc_sets: dict[str, Any]) -> list[str]:
    copied: list[str] = []

    if doc_set == "root_docs":
        for relative_path in doc_sets.get("root_docs", []):
            source = archeia_output / relative_path
            target = worktree / relative_path
            if source.exists():
                copy_entry(source, target)
                copied.append(relative_path)
        return copied

    if doc_set == "archeia":
        source_dir = archeia_output / ".archeia"
        target_dir = worktree / ".archeia"
        if source_dir.exists():
            copy_tree_contents(source_dir, target_dir)
            copied.append(".archeia")
        return copied

    if doc_set == "colocated_readmes":
        bundle_name = "colocated-readmes"
    elif doc_set == "colocated_agents":
        bundle_name = "colocated-agents"
    else:
        raise ValueError(f"Unknown doc set: {doc_set}")

    bundle_root = archeia_output / bundle_name
    for entry in resolve_colocated_entries(bundle_root):
        source = Path(entry["source"])
        target = worktree / entry["target"]
        copy_entry(source, target)
        copied.append(entry["target"])

    return copied


def apply_condition(
    repo_id: str,
    condition_id: str,
    worktree: Path,
    archeia_output: Path,
    conditions_path: Path,
) -> dict[str, Any]:
    doc_sets, condition_map = load_condition_map(conditions_path)
    if condition_id not in condition_map:
        raise KeyError(f"Unknown condition: {condition_id}")

    condition = condition_map[condition_id]
    repo_ids = condition.get("repo_ids", ["*"])
    if repo_id not in repo_ids and "*" not in repo_ids:
        raise ValueError(f"Condition {condition_id} does not apply to repo {repo_id}")

    keep_existing_docs = bool(condition.get("keep_existing_docs", False))
    removed: list[str] = []
    copied: list[str] = []

    if not keep_existing_docs:
        removed = remove_generated_docs(worktree, archeia_output, doc_sets)
        for doc_set in condition.get("include_sets", []):
            copied.extend(apply_doc_set(worktree, archeia_output, doc_set, doc_sets))

    summary = {
        "repo_id": repo_id,
        "condition_id": condition_id,
        "worktree": str(worktree),
        "archeia_output": str(archeia_output),
        "removed_paths": removed,
        "copied_paths": sorted(set(copied)),
        "kept_existing_docs": keep_existing_docs,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply an Archeia evaluation condition to a worktree")
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--archeia-output", required=True)
    parser.add_argument(
        "--conditions-path",
        default=str(Path("evals/config/conditions.yaml")),
    )
    args = parser.parse_args()

    summary = apply_condition(
        repo_id=args.repo_id,
        condition_id=args.condition,
        worktree=Path(args.worktree),
        archeia_output=Path(args.archeia_output),
        conditions_path=Path(args.conditions_path),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
