#!/usr/bin/env bash
set -eo pipefail

usage() {
  cat <<'USAGE'
Usage: discover.sh <repo-root>

Scan a repository and emit a deterministic JSON exploration plan for
archeia-write-tech-docs.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 1
fi

repo_root=$(cd "$1" 2>/dev/null && pwd -P) || {
  echo "error: repo root is not accessible" >&2
  exit 1
}

[[ -d "$repo_root" ]] || {
  echo "error: repo root is not a directory" >&2
  exit 1
}

cd "$repo_root"

json_escape() {
  local value=$1
  value=${value//\\/\\\\}
  value=${value//"/\\"}
  value=${value//$'\n'/\\n}
  value=${value//$'\r'/\\r}
  value=${value//$'\t'/\\t}
  printf '%s' "$value"
}

append_unique() {
  local array_name=$1
  local item=$2
  local count existing i
  eval "count=\${#${array_name}[@]}"
  for ((i = 0; i < count; i++)); do
    eval "existing=\${${array_name}[i]}"
    [[ $existing == "$item" ]] && return
  done
  eval "${array_name}+=(\"\$item\")"
}

emit_array() {
  local array_name=$1
  local count item i
  eval "count=\${#${array_name}[@]}"
  printf '['
  for ((i = 0; i < count; i++)); do
    eval "item=\${${array_name}[i]}"
    (( i > 0 )) && printf ', '
    printf '"%s"' "$(json_escape "$item")"
  done
  printf ']'
}

pruned_find_files() {
  find . \
    \( -type d \( -name .git -o -name node_modules -o -name .next -o -name dist -o -name build -o -name target -o -name coverage -o -name .context -o -name .venv -o -name venv -o -name __pycache__ \) -prune \) \
    -o -type f -print | sed 's#^\./##' | LC_ALL=C sort
}

pruned_find_dirs() {
  find . \
    \( -type d \( -name .git -o -name node_modules -o -name .next -o -name dist -o -name build -o -name target -o -name coverage -o -name .context -o -name .venv -o -name venv -o -name __pycache__ \) -prune \) \
    -o -type d -print | sed 's#^\./##' | awk 'NF' | LC_ALL=C sort
}

declare -a repo_files=()
declare -a repo_dirs=()
declare -a root_manifests=()
declare -a root_configs=()
declare -a schema_and_models=()
declare -a lockfiles_and_workspaces=()
declare -a root_docs=()
declare -a ci_cd=()
declare -a test_setup=()
declare -a source_roots=()
declare -a source_samples=()
declare -a shallow_dirs=()
declare -a files_to_read=()
declare -a migration_sql=()

while IFS= read -r file; do
  [[ -n $file ]] && repo_files+=("$file")
done < <(pruned_find_files)

while IFS= read -r dir; do
  [[ -n $dir ]] && repo_dirs+=("$dir")
done < <(pruned_find_dirs)

for file in "${repo_files[@]}"; do
  case "$file" in
    package.json|pyproject.toml|Cargo.toml|go.mod|Gemfile|composer.json|pom.xml|build.gradle|Mix.exs|deno.json)
      append_unique root_manifests "$file"
      ;;
    tsconfig.json|tsconfig*.json|ruff.toml|.eslintrc*|.prettierrc*|biome.json|Makefile|Justfile|Taskfile.yml|Dockerfile|docker-compose.yml|fly.toml|render.yaml|railway.json|vercel.json|netlify.toml|.tool-versions|.nvmrc|.python-version|.pre-commit-config.yaml)
      if [[ $file != */* ]]; then
        append_unique root_configs "$file"
      fi
      ;;
    pnpm-lock.yaml|package-lock.json|yarn.lock|uv.lock|poetry.lock|Cargo.lock|pnpm-workspace.yaml)
      if [[ $file != */* ]]; then
        append_unique lockfiles_and_workspaces "$file"
      fi
      ;;
    README.md|CONTRIBUTING.md|CHANGELOG.md)
      append_unique root_docs "$file"
      ;;
    .github/workflows/*.yml|.github/workflows/*.yaml|.gitlab-ci.yml|.circleci/config.yml)
      append_unique ci_cd "$file"
      ;;
    tests/conftest.py|jest.config.*|vitest.config.*|test/test_helper.*|.nycrc|pytest.ini|setup.cfg|phpunit.xml)
      append_unique test_setup "$file"
      ;;
    prisma/schema.prisma|schema.graphql)
      append_unique schema_and_models "$file"
      ;;
    */models.py|*/models/*.py|*.entity.ts|*/schema.ts)
      append_unique schema_and_models "$file"
      ;;
    migrations/*.sql|*/migrations/*.sql)
      append_unique migration_sql "$file"
      ;;
  esac
done

count=${#migration_sql[@]}
for ((i = 0; i < count && i < 2; i++)); do
  append_unique schema_and_models "${migration_sql[i]}"
done

for dir in "${repo_dirs[@]}"; do
  case "$dir" in
    packages|apps)
      append_unique lockfiles_and_workspaces "$dir/"
      ;;
    src|lib|app|server|cmd|crates|packages/*/src|apps/*/src)
      append_unique source_roots "$dir"
      ;;
  esac

  slash_count=$(printf '%s' "$dir" | tr -cd '/' | wc -c | tr -d ' ')
  if [[ $dir != '.' && $slash_count -le 1 ]]; then
    append_unique shallow_dirs "$dir"
  fi
done

if [[ ${#source_roots[@]} -gt 0 ]]; then
  for file in "${repo_files[@]}"; do
    for root in "${source_roots[@]}"; do
      if [[ $file == "$root"/* ]]; then
        base=${file##*/}
        case "$base" in
          index.*|main.*|app.*|mod.rs|server.*|cli.*)
            append_unique source_samples "$file"
            ;;
        esac
        break
      fi
    done
  done
fi

has_workspaces=false
if [[ -f package.json ]] && grep -q '"workspaces"' package.json; then
  has_workspaces=true
elif [[ -d packages || -d apps || -f pnpm-workspace.yaml ]]; then
  has_workspaces=true
fi

has_docker=false
if [[ -f Dockerfile || -f docker-compose.yml ]]; then
  has_docker=true
fi

has_tests=false
if [[ -d tests || -d test || -d spec || -d __tests__ || ${#test_setup[@]} -gt 0 ]]; then
  has_tests=true
fi

for item in "${root_manifests[@]}"; do append_unique files_to_read "$item"; done
for item in "${root_configs[@]}"; do append_unique files_to_read "$item"; done
for item in "${schema_and_models[@]}"; do append_unique files_to_read "$item"; done
for item in "${lockfiles_and_workspaces[@]}"; do
  [[ $item == */ ]] && continue
  append_unique files_to_read "$item"
done
for item in "${root_docs[@]}"; do append_unique files_to_read "$item"; done
count=${#ci_cd[@]}
for ((i = 0; i < count && i < 3; i++)); do append_unique files_to_read "${ci_cd[i]}"; done
for item in "${test_setup[@]}"; do append_unique files_to_read "$item"; done
count=${#source_samples[@]}
for ((i = 0; i < count && i < 5; i++)); do append_unique files_to_read "${source_samples[i]}"; done

printf '{\n'
printf '  "repo_root": "%s",\n' "$(json_escape "$repo_root")"
printf '  "files_to_read": '
emit_array files_to_read
printf ',\n'
printf '  "by_priority": {\n'
printf '    "root_manifests": '
emit_array root_manifests
printf ',\n'
printf '    "root_configs": '
emit_array root_configs
printf ',\n'
printf '    "schema_and_models": '
emit_array schema_and_models
printf ',\n'
printf '    "lockfiles_and_workspaces": '
emit_array lockfiles_and_workspaces
printf ',\n'
printf '    "root_docs": '
emit_array root_docs
printf ',\n'
printf '    "ci_cd": '
emit_array ci_cd
printf ',\n'
printf '    "test_setup": '
emit_array test_setup
printf ',\n'
printf '    "source_samples": '
emit_array source_samples
printf '\n'
printf '  },\n'
printf '  "source_roots": '
emit_array source_roots
printf ',\n'
printf '  "shallow_dirs": '
emit_array shallow_dirs
printf ',\n'
printf '  "signals": {\n'
printf '    "has_workspaces": %s,\n' "$has_workspaces"
printf '    "has_docker": %s,\n' "$has_docker"
printf '    "has_tests": %s\n' "$has_tests"
printf '  }\n'
printf '}\n'
