#!/usr/bin/env bash
set -eo pipefail

usage() {
  cat <<'USAGE'
Usage: validate_evidence_fallback.sh <repo-root> [output-dir] [--include-root-docs]

Best-effort evidence validation without python3.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

include_root_docs=false
positional=()
for arg in "$@"; do
  if [[ $arg == "--include-root-docs" ]]; then
    include_root_docs=true
  else
    positional+=("$arg")
  fi
done

if [[ ${#positional[@]} -lt 1 || ${#positional[@]} -gt 2 ]]; then
  usage >&2
  exit 1
fi

repo_root=$(cd "${positional[0]}" 2>/dev/null && pwd -P) || {
  echo "error: repo root is not accessible" >&2
  exit 1
}

if [[ ${#positional[@]} -eq 1 ]]; then
  output_dir="$repo_root/.archeia"
else
  output_dir=$(cd "${positional[1]}" 2>/dev/null && pwd -P) || {
    echo "error: output dir is not accessible" >&2
    exit 1
  }
fi

[[ -d "$output_dir" ]] || {
  echo "error: output dir is not accessible" >&2
  exit 1
}

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

append_malformed() {
  local file=$1
  local reason=$2
  local value=$3
  malformed_evidence+=("{\"file\": \"$(json_escape "$file")\", \"reason\": \"$(json_escape "$reason")\", \"value\": \"$(json_escape "$value")\"}")
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

emit_object_array() {
  local count=${#malformed_evidence[@]}
  local i
  printf '['
  for ((i = 0; i < count; i++)); do
    (( i > 0 )) && printf ', '
    printf '%s' "${malformed_evidence[i]}"
  done
  printf ']'
}

normalize_token() {
  local token=$1
  token=${token#./}
  while [[ $token == ./* ]]; do
    token=${token#./}
  done
  printf '%s' "$token"
}

validate_token() {
  local owner_file=$1
  local token=$2
  local normalized

  normalized=$(normalize_token "$token")
  if [[ -z $normalized ]]; then
    append_malformed "$owner_file" "empty token" "$token"
    return
  fi
  if [[ $normalized == http://* || $normalized == https://* ]]; then
    append_malformed "$owner_file" "url" "$token"
    return
  fi
  case "$normalized" in
    '[files]'|'[file]'|'[file paths]'|'[path]'|'[paths]'|'[manifest]'|'[config file]'|'[config files]'|'[source directory]'|'[source files with patterns]')
      append_malformed "$owner_file" "placeholder token" "$token"
      return
      ;;
  esac
  if [[ $normalized == /* ]]; then
    append_malformed "$owner_file" "absolute path" "$token"
    return
  fi
  if [[ -e "$repo_root/$normalized" ]]; then
    append_unique valid_paths "$normalized"
  else
    append_unique invalid_paths "$normalized"
  fi
}

parse_markdown_file() {
  local file=$1
  checked_files+=("${file#$repo_root/}")
  while IFS=$'\t' read -r _ line_content; do
    [[ -z ${line_content:-} ]] && continue
    local tokens found=0
    tokens=$(printf '%s\n' "$line_content" | grep -o '`[^`][^`]*`' || true)
    if [[ -z $tokens ]]; then
      append_malformed "${file#$repo_root/}" "missing inline code tokens" "$line_content"
      continue
    fi
    while IFS= read -r token; do
      [[ -z $token ]] && continue
      found=1
      token=${token#\`}
      token=${token%\`}
      validate_token "${file#$repo_root/}" "$token"
    done <<< "$tokens"
    if [[ $found -eq 0 ]]; then
      append_malformed "${file#$repo_root/}" "missing inline code tokens" "$line_content"
    fi
  done < <(awk 'BEGIN{fence=0} /^```/ || /^~~~/ {fence=!fence; next} !fence && /^\*\*Evidence:\*\*/ {sub(/^\*\*Evidence:\*\*[[:space:]]*/, "", $0); print FNR "\t" $0}' "$file")
}

process_evidence_buffer() {
  local file=$1
  local buffer=$2
  local body items compact token

  body=$(printf '%s' "$buffer" | sed -e '1s/^[^[]*\[//' -e '$s/\][^]]*$//')
  items=$(printf '%s\n' "$body" | grep -o '"[^"]*"' || true)
  compact=$(printf '%s' "$body" | sed 's/"[^"]*"//g' | tr -d '[:space:],')

  if [[ -n $compact ]]; then
    append_malformed "$file" "fallback parse failure" "$compact"
    return
  fi

  while IFS= read -r token; do
    [[ -z $token ]] && continue
    token=${token#\"}
    token=${token%\"}
    validate_token "$file" "$token"
  done <<< "$items"
}

parse_json_file() {
  local file=$1
  checked_files+=("${file#$repo_root/}")
  local in_array=0
  local buffer=""
  while IFS= read -r line || [[ -n $line ]]; do
    if [[ $in_array -eq 0 ]]; then
      if [[ $line == *'"evidence"'*'['* ]]; then
        in_array=1
        buffer=$line
        if [[ $line == *']'* ]]; then
          process_evidence_buffer "${file#$repo_root/}" "$buffer"
          buffer=""
          in_array=0
        fi
      fi
    else
      buffer+=$'\n'$line
      if [[ $line == *']'* ]]; then
        process_evidence_buffer "${file#$repo_root/}" "$buffer"
        buffer=""
        in_array=0
      fi
    fi
  done < "$file"

  if [[ $in_array -eq 1 ]]; then
    append_malformed "${file#$repo_root/}" "fallback parse failure" "unterminated evidence array"
  fi
}

declare -a checked_files=()
declare -a valid_paths=()
declare -a invalid_paths=()
declare -a malformed_evidence=()
declare -a markdown_files=()
declare -a json_files=()

while IFS= read -r file; do
  markdown_files+=("$file")
done < <(find "$output_dir" -maxdepth 1 -type f -name '*.md' | LC_ALL=C sort)

while IFS= read -r file; do
  json_files+=("$file")
done < <(find "$output_dir" -maxdepth 1 -type f -name '*.json' | LC_ALL=C sort)

for file in "${markdown_files[@]}"; do
  parse_markdown_file "$file"
done

for file in "${json_files[@]}"; do
  parse_json_file "$file"
done

if [[ $include_root_docs == true ]]; then
  for rel in AGENTS.md CLAUDE.md; do
    if [[ -f "$repo_root/$rel" ]]; then
      parse_markdown_file "$repo_root/$rel"
    fi
  done
fi

printf '{\n'
printf '  "mode": "fallback",\n'
printf '  "warning": "Best-effort validation without python3; JSON parsing is conservative.",\n'
printf '  "repo_root": "%s",\n' "$(json_escape "$repo_root")"
printf '  "output_dir": "%s",\n' "$(json_escape "$output_dir")"
printf '  "checked_files": '
emit_array checked_files
printf ',\n'
printf '  "valid_paths": '
emit_array valid_paths
printf ',\n'
printf '  "invalid_paths": '
emit_array invalid_paths
printf ',\n'
printf '  "malformed_evidence": '
emit_object_array
printf ',\n'
printf '  "stats": {\n'
printf '    "checked_files": %s,\n' "${#checked_files[@]}"
printf '    "valid_paths": %s,\n' "${#valid_paths[@]}"
printf '    "invalid_paths": %s,\n' "${#invalid_paths[@]}"
printf '    "malformed_evidence": %s\n' "${#malformed_evidence[@]}"
printf '  }\n'
printf '}\n'

if [[ ${#invalid_paths[@]} -gt 0 || ${#malformed_evidence[@]} -gt 0 ]]; then
  exit 2
fi
