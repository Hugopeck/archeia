#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: validate-evidence.sh <repo-root> [output-dir] [--include-root-docs]

Validate canonical evidence locations in generated archeia docs.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 3 ]]; then
  usage >&2
  exit 1
fi

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if command -v python3 >/dev/null 2>&1; then
  echo "mode=python" >&2
  python3 "$script_dir/validate_evidence.py" "$@"
else
  echo "mode=fallback" >&2
  "$script_dir/validate_evidence_fallback.sh" "$@"
fi
