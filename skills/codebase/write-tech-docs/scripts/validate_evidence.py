#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

PLACEHOLDERS = {"[files]", "[file]", "[file paths]", "[path]", "[paths]", "[manifest]", "[config file]", "[config files]", "[source directory]", "[source files with patterns]"}
EVIDENCE_LINE_RE = re.compile(r"^\*\*Evidence:\*\*\s*(.*)$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def usage() -> None:
    print(
        "Usage: validate_evidence.py <repo-root> [output-dir] [--include-root-docs]",
        file=sys.stderr,
    )


def parse_args(argv: list[str]) -> tuple[Path, Path, bool]:
    if not argv or argv[0] in {"-h", "--help"}:
        usage()
        raise SystemExit(0)

    include_root_docs = False
    positional: list[str] = []
    for arg in argv:
        if arg == "--include-root-docs":
            include_root_docs = True
        else:
            positional.append(arg)

    if len(positional) < 1 or len(positional) > 2:
        usage()
        raise SystemExit(1)

    repo_root = Path(positional[0]).expanduser().resolve()
    if not repo_root.is_dir():
        print("error: repo root is not accessible", file=sys.stderr)
        raise SystemExit(1)

    output_dir = (repo_root / ".archeia") if len(positional) == 1 else Path(positional[1]).expanduser().resolve()
    if not output_dir.is_dir():
        print("error: output dir is not accessible", file=sys.stderr)
        raise SystemExit(1)

    return repo_root, output_dir, include_root_docs


def normalize_token(token: str) -> tuple[str | None, str | None]:
    value = token.strip()
    if not value:
        return None, "empty token"
    if value.startswith(("http://", "https://")):
        return None, "url"
    if value in PLACEHOLDERS or re.fullmatch(r"\[[^\]]+\]", value):
        return None, "placeholder token"
    if os.path.isabs(value):
        return None, "absolute path"
    while value.startswith("./"):
        value = value[2:]
    normalized = os.path.normpath(value)
    if normalized == ".":
        return None, "empty token"
    return normalized, None


def repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def parse_markdown(path: Path, repo_root: Path, malformed: list[dict], valid_paths: list[str], invalid_paths: list[str]) -> None:
    in_fence = False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"error: failed to read {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = EVIDENCE_LINE_RE.match(stripped)
        if not match:
            continue

        payload = match.group(1)
        tokens = INLINE_CODE_RE.findall(payload)
        if not tokens:
            malformed.append(
                {
                    "file": repo_relative(path, repo_root),
                    "reason": "missing inline code tokens",
                    "value": payload.strip(),
                }
            )
            continue

        for token in tokens:
            normalized, reason = normalize_token(token)
            if reason:
                malformed.append(
                    {
                        "file": repo_relative(path, repo_root),
                        "reason": reason,
                        "value": token,
                    }
                )
                continue
            candidate = repo_root / normalized
            if candidate.exists():
                if normalized not in valid_paths:
                    valid_paths.append(normalized)
            else:
                if normalized not in invalid_paths:
                    invalid_paths.append(normalized)


def walk_json(node, path: Path, repo_root: Path, malformed: list[dict], valid_paths: list[str], invalid_paths: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "evidence":
                if not isinstance(value, list):
                    malformed.append(
                        {
                            "file": repo_relative(path, repo_root),
                            "reason": "evidence must be an array of strings",
                            "value": type(value).__name__,
                        }
                    )
                    continue
                for item in value:
                    if not isinstance(item, str):
                        malformed.append(
                            {
                                "file": repo_relative(path, repo_root),
                                "reason": "evidence item must be a string",
                                "value": json.dumps(item),
                            }
                        )
                        continue
                    normalized, reason = normalize_token(item)
                    if reason:
                        malformed.append(
                            {
                                "file": repo_relative(path, repo_root),
                                "reason": reason,
                                "value": item,
                            }
                        )
                        continue
                    candidate = repo_root / normalized
                    if candidate.exists():
                        if normalized not in valid_paths:
                            valid_paths.append(normalized)
                    else:
                        if normalized not in invalid_paths:
                            invalid_paths.append(normalized)
            else:
                walk_json(value, path, repo_root, malformed, valid_paths, invalid_paths)
    elif isinstance(node, list):
        for item in node:
            walk_json(item, path, repo_root, malformed, valid_paths, invalid_paths)


def parse_json(path: Path, repo_root: Path, malformed: list[dict], valid_paths: list[str], invalid_paths: list[str]) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: failed to parse {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)
    walk_json(data, path, repo_root, malformed, valid_paths, invalid_paths)


def main(argv: list[str]) -> int:
    repo_root, output_dir, include_root_docs = parse_args(argv)

    checked_files: list[str] = []
    valid_paths: list[str] = []
    invalid_paths: list[str] = []
    malformed: list[dict] = []

    markdown_files = sorted(output_dir.glob("*.md"))
    json_files = sorted(output_dir.glob("*.json"))

    for path in markdown_files + json_files:
        checked_files.append(repo_relative(path, repo_root))
        if path.suffix == ".md":
            parse_markdown(path, repo_root, malformed, valid_paths, invalid_paths)
        else:
            parse_json(path, repo_root, malformed, valid_paths, invalid_paths)

    if include_root_docs:
        for rel in ("AGENTS.md", "CLAUDE.md"):
            path = repo_root / rel
            if not path.exists():
                continue
            checked_files.append(rel)
            parse_markdown(path, repo_root, malformed, valid_paths, invalid_paths)

    result = {
        "mode": "python",
        "repo_root": str(repo_root),
        "output_dir": str(output_dir),
        "checked_files": checked_files,
        "valid_paths": valid_paths,
        "invalid_paths": invalid_paths,
        "malformed_evidence": malformed,
        "stats": {
            "checked_files": len(checked_files),
            "valid_paths": len(valid_paths),
            "invalid_paths": len(invalid_paths),
            "malformed_evidence": len(malformed),
        },
    }

    print(json.dumps(result, indent=2))
    if invalid_paths or malformed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
