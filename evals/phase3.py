from __future__ import annotations

# NOTE: migration debt — this module is from the pre-monorepo era and still
# assumes the flat .archeia/<Name>.md|.json layout plus old archeia-<name>
# skill directories under skills/. It needs updating to the standard-compliant
# .archeia/codebase/** layout and skills/codebase/<name>/ structure before it
# can regenerate canonical bundles against the migrated skills. Specifically:
#   - collect_archeia_files (below): hardcodes ".archeia/<name>" and
#     ".archeia/diagrams"; needs to understand .archeia/codebase/**.
#   - skill_prompt_path (below): looks up skills/<name>/SKILL.md; needs to
#     resolve skills/<domain>/<name>/SKILL.md (search across domain subdirs).
#   - validate_phase3_outputs line ~315: hardcodes
#     skills/archeia-write-tech-docs/scripts/validate-evidence.sh; needs
#     skills/codebase/write-tech-docs/scripts/validate-evidence.sh.
#   - All evals/config/bundles/*.yaml bundle specs still use bare old names
#     like "Architecture.md" in required_outputs.archeia and pipeline_order.
# Not on the hot path — only runs when regenerating canonical bundles via
# capture_phase3_bundle / prepare_phase3_workspace. Existing bundles under
# evals/archeia-output/ were migrated in-place in commit de1d83e. The failing
# unit test in evals/tests/test_phase3.py is skipped until this debt is paid.
# Defer to Phase 3+.

import shutil
import tempfile
from pathlib import Path
from typing import Any

from evals.common import EVALS_ROOT, REPO_ROOT, ensure_directory, load_data_file, run_command, utc_now, write_json
from evals.harness.runner import create_worktree, remove_worktree, repo_map


WORKSPACE_METADATA_PATH = Path(".archeia-eval/phase3-workspace.json")
INSTRUCTIONS_PATH = Path(".archeia-eval/phase3-instructions.txt")
SUBAGENT_PACKET_PATH = Path(".archeia-eval/subagent-packet.md")
COLOCATED_AGENT_FILENAMES = {"agents.md", "claude.md"}
COLOCATED_README_FILENAME = "README.md"


def bundle_spec_path(bundles_root: Path, repo_id: str) -> Path:
    return bundles_root / f"{repo_id}.yaml"


def load_repo(repo_id: str, repos_path: Path) -> dict[str, Any]:
    repos = repo_map(repos_path)
    if repo_id not in repos:
        raise KeyError(f"Unknown repo: {repo_id}")
    return repos[repo_id]


def load_bundle_spec(repo_id: str, bundles_root: Path) -> dict[str, Any]:
    path = bundle_spec_path(bundles_root, repo_id)
    if not path.exists():
        raise FileNotFoundError(f"Missing bundle spec: {path}")
    payload = load_data_file(path)
    if payload.get("repo_id") != repo_id:
        raise ValueError(f"Bundle spec {path} repo_id does not match {repo_id}")
    return payload


def skill_prompt_path(skill_name: str, skills_root: Path | None = None) -> Path:
    root = skills_root or (REPO_ROOT / "skills")
    return root / skill_name / "SKILL.md"


def load_skill_prompt(skill_name: str, skills_root: Path | None = None) -> str:
    path = skill_prompt_path(skill_name, skills_root)
    if not path.exists():
        raise FileNotFoundError(f"Missing skill definition: {path}")
    return path.read_text(encoding="utf-8")


def planned_worktree_path(repo_id: str, work_root: Path | None = None) -> Path:
    if work_root is not None:
        return work_root / repo_id
    root = Path(tempfile.mkdtemp(prefix=f"archeia-phase3-{repo_id}-"))
    return root / repo_id


def workspace_metadata_payload(
    repo_id: str,
    repo: dict[str, Any],
    bundle_spec: dict[str, Any],
    worktree: Path,
) -> dict[str, Any]:
    return {
        "repo_id": repo_id,
        "source_path": repo["source_path"],
        "commit": repo["commit"],
        "worktree": str(worktree),
        "pipeline_order": bundle_spec.get("pipeline_order", []),
        "bundle_spec_path": str(bundle_spec_path(EVALS_ROOT / "config" / "bundles", repo_id)),
        "prepared_at": utc_now(),
    }


def build_subagent_packet(bundle_spec: dict[str, Any], worktree: Path, skills_root: Path | None = None) -> str:
    pipeline_order = bundle_spec.get("pipeline_order", [])
    header = [
        "# Archeia Phase 3 Subagent Packet",
        "",
        "You are generating canonical Archeia outputs inside the target repository.",
        "Do not invoke installed slash-command skills.",
        "Instead, follow the embedded `SKILL.md` contents below in the declared order.",
        f"Worktree: `{worktree}`",
        "",
        "Execution rules:",
        "- Work only in the target worktree.",
        "- Run the six phases in order; later phases may depend on earlier artifacts.",
        "- Produce files in place inside the target repo.",
        "- Do not commit changes.",
        "- When an always-attempted output cannot be evidenced, skip the file and leave the insufficiency outcome in the generated docs rather than fabricating it.",
        "- At the end, summarize generated files, skipped outputs, and any evidence gaps.",
        "",
    ]

    sections: list[str] = []
    for index, skill_name in enumerate(pipeline_order, start=1):
        prompt = load_skill_prompt(skill_name, skills_root).rstrip()
        sections.extend(
            [
                f"## Step {index}: {skill_name}",
                "",
                f"Source: `{skill_prompt_path(skill_name, skills_root)}`",
                "",
                prompt,
                "",
            ]
        )

    return "\n".join(header + sections).rstrip() + "\n"


def write_subagent_packet(worktree: Path, bundle_spec: dict[str, Any], skills_root: Path | None = None) -> Path:
    path = worktree / SUBAGENT_PACKET_PATH
    ensure_directory(path.parent)
    path.write_text(build_subagent_packet(bundle_spec, worktree, skills_root), encoding="utf-8")
    return path


def build_workspace_instructions(
    worktree: Path,
    bundle_spec: dict[str, Any],
    packet_path: Path,
) -> str:
    pipeline_order = bundle_spec.get("pipeline_order", [])
    ordered_steps = "\n".join(f"{index}. {name}" for index, name in enumerate(pipeline_order, start=1))
    return (
        "Phase 3 operator checklist\n\n"
        f"Worktree: {worktree}\n"
        f"Subagent packet: {packet_path}\n\n"
        "1. Start a subagent rooted at this worktree.\n"
        "2. Give the subagent this wrapper prompt:\n\n"
        "   Run the Archeia Phase 3 pipeline in this repository. Do not use installed skills. "
        "Follow the attached packet exactly in order, applying each embedded SKILL.md to this repo. "
        "Stop after all six steps are complete and summarize generated files, skipped attempted outputs, and evidence gaps.\n\n"
        "3. Paste the full contents of the subagent packet into that subagent.\n"
        "4. Wait for the subagent to finish and inspect the generated outputs.\n"
        "5. From the Archeia repo, run the capture script to extract the canonical bundle.\n\n"
        "Declared pipeline order:\n"
        f"{ordered_steps}\n"
    )


def write_workspace_instructions(
    worktree: Path,
    bundle_spec: dict[str, Any],
    packet_path: Path,
) -> Path:
    path = worktree / INSTRUCTIONS_PATH
    ensure_directory(path.parent)
    path.write_text(build_workspace_instructions(worktree, bundle_spec, packet_path), encoding="utf-8")
    return path


def render_phase3_subagent_packet(
    repo_id: str,
    repos_path: Path | None = None,
    bundles_root: Path | None = None,
    worktree: Path | None = None,
    skills_root: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    repos_path = repos_path or (EVALS_ROOT / "config" / "repos.yaml")
    bundles_root = bundles_root or (EVALS_ROOT / "config" / "bundles")
    repo = load_repo(repo_id, repos_path)
    bundle_spec = load_bundle_spec(repo_id, bundles_root)
    target_worktree = worktree or planned_worktree_path(repo_id)
    packet = build_subagent_packet(bundle_spec, target_worktree, skills_root)

    if output_path is not None:
        ensure_directory(output_path.parent)
        output_path.write_text(packet, encoding="utf-8")

    return {
        "repo_id": repo_id,
        "source_path": repo["source_path"],
        "commit": repo["commit"],
        "worktree": str(target_worktree),
        "pipeline_order": bundle_spec.get("pipeline_order", []),
        "packet_path": str(output_path) if output_path is not None else None,
        "packet": packet,
    }


def prepare_phase3_workspace(
    repo_id: str,
    repos_path: Path | None = None,
    bundles_root: Path | None = None,
    work_root: Path | None = None,
    skills_root: Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    repos_path = repos_path or (EVALS_ROOT / "config" / "repos.yaml")
    bundles_root = bundles_root or (EVALS_ROOT / "config" / "bundles")
    repo = load_repo(repo_id, repos_path)
    bundle_spec = load_bundle_spec(repo_id, bundles_root)
    worktree = planned_worktree_path(repo_id, work_root)

    source_repo = Path(repo["source_path"])
    if worktree.exists():
        if not force:
            raise FileExistsError(f"Worktree already exists: {worktree}")
        remove_worktree(source_repo, worktree)

    create_worktree(source_repo, repo["commit"], worktree)

    metadata = workspace_metadata_payload(repo_id, repo, bundle_spec, worktree)
    metadata_path = worktree / WORKSPACE_METADATA_PATH
    write_json(metadata_path, metadata)
    packet_path = write_subagent_packet(worktree, bundle_spec, skills_root)
    instructions_path = write_workspace_instructions(worktree, bundle_spec, packet_path)

    return {
        "repo_id": repo_id,
        "source_path": repo["source_path"],
        "commit": repo["commit"],
        "worktree": str(worktree),
        "metadata_path": str(metadata_path),
        "packet_path": str(packet_path),
        "instructions_path": str(instructions_path),
        "pipeline_order": bundle_spec.get("pipeline_order", []),
    }


def parse_git_status_lines(raw: str) -> list[str]:
    paths: list[str] = []
    for line in raw.splitlines():
        if not line:
            continue
        payload = line[3:]
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        paths.append(payload)
    return paths


def changed_paths(worktree: Path) -> list[str]:
    result = run_command(["git", "status", "--short"], cwd=worktree, timeout=60)
    if result["exit_code"] != 0:
        raise RuntimeError(f"git status failed: {result['stderr']}")
    return parse_git_status_lines(result["stdout"])


def collect_colocated_manifest_entries(paths: list[str], predicate: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for relative_path in sorted(set(paths)):
        file_path = Path(relative_path)
        if len(file_path.parts) < 2:
            continue
        filename = file_path.name
        if predicate == "readmes":
            if filename != COLOCATED_README_FILENAME:
                continue
        elif predicate == "agents":
            if filename not in COLOCATED_AGENT_FILENAMES:
                continue
        else:
            raise ValueError(f"Unknown predicate: {predicate}")
        entries.append({"source": file_path.as_posix(), "target": file_path.as_posix()})
    return entries


def copy_manifest_entries(worktree: Path, bundle_root: Path, entries: list[dict[str, str]]) -> None:
    for entry in entries:
        source = worktree / entry["target"]
        destination = bundle_root / entry["source"]
        ensure_directory(destination.parent)
        shutil.copy2(source, destination)


def collect_archeia_files(worktree: Path, bundle_spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    archeia_root = worktree / ".archeia"
    if not archeia_root.exists():
        raise FileNotFoundError(f"Missing .archeia directory in {worktree}")

    copy_rules = bundle_spec.get("copy_rules", {})
    excluded = set(copy_rules.get("exclude", []))
    required_files = bundle_spec.get("required_outputs", {}).get("archeia", [])
    always_attempted = bundle_spec.get("always_attempted_outputs", [])
    conditional = list(bundle_spec.get("conditional_expectations", {}).keys())

    copied: list[str] = []
    skipped: list[str] = []
    for name in required_files + always_attempted + conditional:
        relative = f".archeia/{name}"
        if relative in excluded:
            continue
        path = worktree / relative
        if name in required_files and not path.exists():
            raise FileNotFoundError(f"Missing required output: {path}")
        if path.exists():
            copied.append(relative)
        else:
            skipped.append(relative)

    diagrams_path = archeia_root / "diagrams"
    if diagrams_path.exists() and ".archeia/diagrams" not in excluded:
        copied.append(".archeia/diagrams")

    return sorted(set(copied)), sorted(set(skipped))


def copy_archeia_outputs(worktree: Path, bundle_root: Path, archeia_paths: list[str]) -> None:
    for relative in archeia_paths:
        source = worktree / relative
        destination = bundle_root / relative
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            ensure_directory(destination.parent)
            shutil.copy2(source, destination)


def validate_phase3_outputs(worktree: Path, include_root_docs: bool = True) -> dict[str, Any]:
    script = REPO_ROOT / "skills" / "archeia-write-tech-docs" / "scripts" / "validate-evidence.sh"
    command = ["bash", str(script), str(worktree), str(worktree / ".archeia")]
    if include_root_docs:
        command.append("--include-root-docs")
    result = run_command(command, cwd=REPO_ROOT, timeout=300)
    status = "ok"
    if result["exit_code"] == 2:
        status = "invalid"
    elif result["exit_code"] != 0:
        status = "error"
    return {
        "status": status,
        "exit_code": result["exit_code"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "command": command,
    }


def load_workspace_metadata(worktree: Path) -> dict[str, Any] | None:
    path = worktree / WORKSPACE_METADATA_PATH
    if not path.exists():
        return None
    return load_data_file(path)


def assert_expected_head(worktree: Path, expected_commit: str) -> str:
    result = run_command(["git", "rev-parse", "HEAD"], cwd=worktree, timeout=60)
    if result["exit_code"] != 0:
        raise RuntimeError(f"git rev-parse failed: {result['stderr']}")
    head = result["stdout"].strip()
    if head != expected_commit:
        raise ValueError(f"Worktree HEAD {head} does not match pinned commit {expected_commit}")
    return head


def capture_phase3_bundle(
    repo_id: str,
    worktree: Path,
    repos_path: Path | None = None,
    bundles_root: Path | None = None,
    bundle_root: Path | None = None,
    force: bool = False,
    allow_invalid_evidence: bool = False,
) -> dict[str, Any]:
    repos_path = repos_path or (EVALS_ROOT / "config" / "repos.yaml")
    bundles_root = bundles_root or (EVALS_ROOT / "config" / "bundles")
    repo = load_repo(repo_id, repos_path)
    bundle_spec = load_bundle_spec(repo_id, bundles_root)
    bundle_root = bundle_root or (EVALS_ROOT / "archeia-output" / repo_id)

    if bundle_root.exists():
        if not force:
            raise FileExistsError(f"Bundle already exists: {bundle_root}")
        shutil.rmtree(bundle_root)

    head = assert_expected_head(worktree, repo["commit"])
    validation = validate_phase3_outputs(worktree, include_root_docs=True)
    if validation["status"] == "error":
        raise RuntimeError(f"Evidence validation failed: {validation['stderr']}")
    if validation["status"] == "invalid" and not allow_invalid_evidence:
        raise ValueError(
            "Evidence validation reported invalid references; rerun with --allow-invalid-evidence to capture anyway"
        )

    ensure_directory(bundle_root / ".archeia")
    ensure_directory(bundle_root / "colocated-readmes")
    ensure_directory(bundle_root / "colocated-agents")

    copy_rules = bundle_spec.get("copy_rules", {})

    copied_root_docs: list[str] = []
    if copy_rules.get("include_root_docs", True):
        for name in bundle_spec.get("required_outputs", {}).get("root_docs", []):
            source = worktree / name
            if not source.exists():
                raise FileNotFoundError(f"Missing required root doc: {source}")
            shutil.copy2(source, bundle_root / name)
            copied_root_docs.append(name)

    copied_archeia: list[str] = []
    skipped_archeia: list[str] = []
    if copy_rules.get("include_archeia_dir", True):
        copied_archeia, skipped_archeia = collect_archeia_files(worktree, bundle_spec)
        copy_archeia_outputs(worktree, bundle_root, copied_archeia)

    diff_paths = changed_paths(worktree)
    readme_entries: list[dict[str, str]] = []
    if copy_rules.get("include_colocated_readmes", False):
        readme_entries = collect_colocated_manifest_entries(diff_paths, "readmes")
    agent_entries: list[dict[str, str]] = []
    if copy_rules.get("include_colocated_agents", False):
        agent_entries = collect_colocated_manifest_entries(diff_paths, "agents")
    copy_manifest_entries(worktree, bundle_root / "colocated-readmes", readme_entries)
    copy_manifest_entries(worktree, bundle_root / "colocated-agents", agent_entries)
    write_json(bundle_root / "colocated-readmes" / "manifest.json", readme_entries)
    write_json(bundle_root / "colocated-agents" / "manifest.json", agent_entries)

    manifest = {
        "repo_id": repo_id,
        "source_repo": repo["repo"],
        "source_path": repo["source_path"],
        "pinned_commit": repo["commit"],
        "captured_head": head,
        "captured_at": utc_now(),
        "worktree": str(worktree),
        "pipeline_order": bundle_spec.get("pipeline_order", []),
        "copied_root_docs": copied_root_docs,
        "copied_archeia_paths": copied_archeia,
        "skipped_outputs": skipped_archeia,
        "colocated_readmes": [entry["target"] for entry in readme_entries],
        "colocated_agents": [entry["target"] for entry in agent_entries],
        "validation": validation,
    }
    write_json(bundle_root / "bundle-manifest.json", manifest)

    return {
        "repo_id": repo_id,
        "bundle_root": str(bundle_root),
        "copied_root_docs": copied_root_docs,
        "copied_archeia_paths": copied_archeia,
        "skipped_outputs": skipped_archeia,
        "colocated_readmes": len(readme_entries),
        "colocated_agents": len(agent_entries),
        "validation_status": validation["status"],
    }


def cleanup_phase3_workspace(repo_id: str, worktree: Path, repos_path: Path | None = None) -> dict[str, Any]:
    repos_path = repos_path or (EVALS_ROOT / "config" / "repos.yaml")
    repo = load_repo(repo_id, repos_path)
    remove_worktree(Path(repo["source_path"]), worktree)
    return {"repo_id": repo_id, "worktree": str(worktree), "removed": not worktree.exists()}
