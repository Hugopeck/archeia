#!/usr/bin/env bash
# git-scanner.sh — Collect git history data for archeia-scan-git.
#
# Runs 5-6 git log passes over the repository and writes clean TSV files
# to an output directory. The calling agent reads these TSVs to build
# .archeia/codebase/git-report.md without needing to construct complex awk pipelines.
#
# Author aliasing: contributors who use multiple git configs (different
# name/email combos) are unified by email. The most recent name associated
# with each email is used as the canonical display name. An aliases.tsv
# file is produced so the agent can see the mapping.
#
# Usage:
#   bash git-scanner.sh [--since YYYY-MM-DD] [--output-dir DIR]
#
# Options:
#   --since        Limit history to commits after this date (for large repos)
#   --output-dir   Directory for TSV output (default: /tmp/archeia-scan-git-$$)
#
# Output files:
#   aliases.tsv           email | canonical_name
#   roster.tsv            author | commits | added | deleted | first_date | last_date
#   monthly.tsv           month | author | commits | added | deleted
#   yearly.tsv            year | author | commits | added | deleted
#   file_churn.tsv        file | added | deleted | commit_count
#   file_authors.tsv      file | directory | author  (deduplicated)
#   dir_authors.tsv       directory | author | commit_count
#   merges.tsv            hash | author | committer | date | subject
#   coauthors.tsv         commit_author | coauthor_name | hash
#   time_patterns.tsv     day_of_week | hour
#   subjects.tsv          hash | date | subject
#   fix_after_fix.tsv     file | occurrences  (only if conventional commits)
#   cross_dir_commits.tsv count  (single value)
#   reverts.tsv           date | month | subject
#   preflight.tsv         key | value
#
# All TSVs use tab as delimiter. No headers — field order is documented above.
# All author fields contain canonical display names (resolved via aliases.tsv).

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
SINCE=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --since)    SINCE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

OUTPUT_DIR="${OUTPUT_DIR:-/tmp/archeia-scan-git-$$}"
mkdir -p "$OUTPUT_DIR"

# Build optional --since flag for git log
SINCE_FLAG=""
if [[ -n "$SINCE" ]]; then
  SINCE_FLAG="--since=$SINCE"
fi

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'not_a_repo\ttrue\n' > "$OUTPUT_DIR/preflight.tsv"
  echo "$OUTPUT_DIR"
  exit 0
fi

COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
IS_SHALLOW=$(git rev-parse --is-shallow-repository 2>/dev/null || echo false)
FIRST_COMMIT_DATE=""
if [[ "$COMMIT_COUNT" -gt 0 ]]; then
  FIRST_COMMIT_DATE=$(git log --reverse --format='%aI' | head -1)
fi

{
  printf 'commit_count\t%s\n' "$COMMIT_COUNT"
  printf 'is_shallow\t%s\n' "$IS_SHALLOW"
  printf 'first_commit_date\t%s\n' "$FIRST_COMMIT_DATE"
} > "$OUTPUT_DIR/preflight.tsv"

if [[ "$COMMIT_COUNT" -eq 0 ]]; then
  echo "$OUTPUT_DIR"
  exit 0
fi

# ---------------------------------------------------------------------------
# Author Alias Map
# ---------------------------------------------------------------------------
# Build a mapping from lowercase email to canonical display name.
# For each email, the name from the most recent commit wins.
# This handles contributors who change their git config over time
# (e.g., "pabdelhay" vs "Pablo Abdelhay", "Filipe" vs "FilipePhys").
ALIASES_FILE="$OUTPUT_DIR/aliases.tsv"

git log --format='%aE|%aN|%aI' $SINCE_FLAG | awk -F'|' '
BEGIN { OFS="\t" }
{
  email = tolower($1)
  name = $2
  date = $3
  if (!(email in latest) || date > latest[email]) {
    latest[email] = date
    canonical[email] = name
  }
}
END {
  for (e in canonical) print e, canonical[e]
}
' > "$ALIASES_FILE"

# Also build committer alias map (for merge author vs committer comparison)
git log --merges --format='%cE|%cN|%aI' $SINCE_FLAG 2>/dev/null | awk -F'|' '
BEGIN { OFS="\t" }
{
  email = tolower($1)
  name = $2
  date = $3
  if (!(email in latest) || date > latest[email]) {
    latest[email] = date
    canonical[email] = name
  }
}
END {
  for (e in canonical) print e, canonical[e]
}
' >> "$ALIASES_FILE"

# Deduplicate aliases (keep last occurrence = committer overrides if newer)
sort -t$'\t' -k1,1 -u "$ALIASES_FILE" -o "$ALIASES_FILE"

# ---------------------------------------------------------------------------
# Pass A — The big one
# Extracts: roster, monthly, yearly, file_churn, subjects
# Uses email (%aE) and resolves to canonical name via aliases.
# ---------------------------------------------------------------------------
git log --format="COMMIT|%H|%aE|%aI|%s" --numstat --no-merges $SINCE_FLAG | awk -F'\t' '
BEGIN {
  OFS="\t"
  # Load alias map
  while ((getline line < "'"$ALIASES_FILE"'") > 0) {
    split(line, parts, "\t")
    alias[parts[1]] = parts[2]
  }
}

function resolve(email) {
  e = tolower(email)
  if (e in alias) return alias[e]
  return email
}

/^COMMIT\|/ {
  n = split($0, parts, "|")
  hash = parts[2]
  raw_author = parts[3]
  author = resolve(raw_author)
  date = parts[4]
  subject = ""
  for (i = 5; i <= n; i++) {
    if (i > 5) subject = subject "|"
    subject = subject parts[i]
  }

  month = substr(date, 1, 7)
  year = substr(date, 1, 4)

  # Roster
  roster_commits[author]++
  if (!(author in roster_first) || date < roster_first[author]) {
    roster_first[author] = date
  }
  if (!(author in roster_last) || date > roster_last[author]) {
    roster_last[author] = date
  }

  # Monthly
  mkey = month SUBSEP author
  monthly_commits[mkey]++

  # Yearly
  ykey = year SUBSEP author
  yearly_commits[ykey]++

  # Subject
  print hash, substr(date,1,10), subject > "'"$OUTPUT_DIR/subjects.tsv"'"

  next
}

/^[0-9]/ {
  added = $1
  deleted = $2
  file = $3
  if (file == "") next

  roster_added[author] += added
  roster_deleted[author] += deleted

  mkey = month SUBSEP author
  monthly_added[mkey] += added
  monthly_deleted[mkey] += deleted

  ykey = year SUBSEP author
  yearly_added[ykey] += added
  yearly_deleted[ykey] += deleted

  file_added[file] += added
  file_deleted[file] += deleted
  file_commits[file]++

  next
}

END {
  for (a in roster_commits) {
    print a, roster_commits[a], roster_added[a]+0, roster_deleted[a]+0, roster_first[a], roster_last[a] > "'"$OUTPUT_DIR/roster.tsv"'"
  }

  for (key in monthly_commits) {
    split(key, mp, SUBSEP)
    print mp[1], mp[2], monthly_commits[key], monthly_added[key]+0, monthly_deleted[key]+0 > "'"$OUTPUT_DIR/monthly.tsv"'"
  }

  for (key in yearly_commits) {
    split(key, yp, SUBSEP)
    print yp[1], yp[2], yearly_commits[key], yearly_added[key]+0, yearly_deleted[key]+0 > "'"$OUTPUT_DIR/yearly.tsv"'"
  }

  for (f in file_commits) {
    print f, file_added[f]+0, file_deleted[f]+0, file_commits[f] > "'"$OUTPUT_DIR/file_churn.tsv"'"
  }
}
'

# ---------------------------------------------------------------------------
# Pass B — Merge commits (with email-based aliasing)
# ---------------------------------------------------------------------------
git log --merges --format='%H|%aE|%cE|%aI|%s' $SINCE_FLAG | awk -F'|' '
BEGIN {
  OFS="\t"
  while ((getline line < "'"$ALIASES_FILE"'") > 0) {
    split(line, parts, "\t")
    alias[parts[1]] = parts[2]
  }
}
function resolve(email) {
  e = tolower(email)
  if (e in alias) return alias[e]
  return email
}
{
  hash = $1
  author = resolve($2)
  committer = resolve($3)
  date = $4
  subject = ""
  for (i = 5; i <= NF; i++) {
    if (i > 5) subject = subject "|"
    subject = subject $i
  }
  print hash, author, committer, date, subject
}
' > "$OUTPUT_DIR/merges.tsv"

# ---------------------------------------------------------------------------
# Pass C — File-to-author mapping (email-based aliasing)
# ---------------------------------------------------------------------------
git log --format='COMMIT_BY:%aE' --name-only --no-merges $SINCE_FLAG | awk '
BEGIN {
  OFS="\t"
  while ((getline line < "'"$ALIASES_FILE"'") > 0) {
    split(line, parts, "\t")
    alias[parts[1]] = parts[2]
  }
}
function resolve(email) {
  e = tolower(email)
  if (e in alias) return alias[e]
  return email
}

/^COMMIT_BY:/ {
  author = resolve(substr($0, 11))
  next
}

/^$/ { next }

{
  file = $0

  idx = index(file, "/")
  if (idx > 0) {
    dir = substr(file, 1, idx - 1)
  } else {
    dir = "(root)"
  }

  fa_key = file SUBSEP author
  if (!(fa_key in fa_seen)) {
    fa_seen[fa_key] = 1
    print file, dir, author > "'"$OUTPUT_DIR/file_authors.tsv"'"
  }

  da_key = dir SUBSEP author
  dir_author_commits[da_key]++
}

END {
  for (key in dir_author_commits) {
    split(key, parts, SUBSEP)
    print parts[1], parts[2], dir_author_commits[key] > "'"$OUTPUT_DIR/dir_authors.tsv"'"
  }
}
'

# ---------------------------------------------------------------------------
# Pass D — Co-author trailers (email-based aliasing)
# ---------------------------------------------------------------------------
git log --format='COMMIT_START|%H|%aE%n%b%nCOMMIT_END' --no-merges $SINCE_FLAG | awk '
BEGIN {
  OFS="\t"
  while ((getline line < "'"$ALIASES_FILE"'") > 0) {
    split(line, parts, "\t")
    alias[parts[1]] = parts[2]
  }
}
function resolve(email) {
  e = tolower(email)
  if (e in alias) return alias[e]
  return email
}

/^COMMIT_START\|/ {
  split($0, parts, "|")
  hash = parts[2]
  author = resolve(parts[3])
  next
}

/^COMMIT_END$/ { next }

{
  line = $0
  lower = tolower(line)
  if (index(lower, "co-authored-by:") == 1) {
    coauthor_raw = line
    sub(/^[Cc][Oo]-[Aa][Uu][Tt][Hh][Oo][Rr][Ee][Dd]-[Bb][Yy]:[ \t]*/, "", coauthor_raw)

    # Try to extract email for alias lookup
    coauthor_email = ""
    if (match(coauthor_raw, /<[^>]+>/)) {
      coauthor_email = substr(coauthor_raw, RSTART+1, RLENGTH-2)
    }

    # Resolve via email if possible, otherwise use raw name
    if (coauthor_email != "" && tolower(coauthor_email) in alias) {
      coauthor = alias[tolower(coauthor_email)]
    } else {
      coauthor = coauthor_raw
      sub(/ *<[^>]*>.*/, "", coauthor)
      gsub(/^[ \t]+|[ \t]+$/, "", coauthor)
    }

    if (coauthor != "" && coauthor != author) {
      dedup_key = author SUBSEP coauthor SUBSEP hash
      if (!(dedup_key in seen_ca)) {
        seen_ca[dedup_key] = 1
        print author, coauthor, hash
      }
    }
  }
}
' > "$OUTPUT_DIR/coauthors.tsv"

# ---------------------------------------------------------------------------
# Pass E — Time patterns (UTC) — no author needed
# ---------------------------------------------------------------------------
TZ=UTC git log --format='%cd' --date=format:'%A|%H' --no-merges $SINCE_FLAG | awk -F'|' '
BEGIN { OFS="\t" }
{ print $1, $2 }
' > "$OUTPUT_DIR/time_patterns.tsv"

# ---------------------------------------------------------------------------
# Pass F — Fix-after-fix detection (conditional)
# ---------------------------------------------------------------------------
TOTAL_SUBJECTS=$(wc -l < "$OUTPUT_DIR/subjects.tsv" 2>/dev/null || echo 0)
CONVENTIONAL_COUNT=0
if [[ "$TOTAL_SUBJECTS" -gt 0 ]]; then
  CONVENTIONAL_COUNT=$(awk -F'\t' '{
    sub(/^[^\t]*\t[^\t]*\t/, "")
    if ($0 ~ /^(feat|fix|chore|docs|style|refactor|perf|test|ci|build|revert)[(:!]/) count++
  } END { print count+0 }' "$OUTPUT_DIR/subjects.tsv")
fi

HAS_CONVENTIONAL="false"
if [[ "$TOTAL_SUBJECTS" -gt 0 ]]; then
  THRESHOLD=$((TOTAL_SUBJECTS * 20 / 100))
  if [[ "$CONVENTIONAL_COUNT" -ge "$THRESHOLD" ]]; then
    HAS_CONVENTIONAL="true"
  fi
fi
printf 'has_conventional\t%s\n' "$HAS_CONVENTIONAL" >> "$OUTPUT_DIR/preflight.tsv"
printf 'conventional_count\t%s\n' "$CONVENTIONAL_COUNT" >> "$OUTPUT_DIR/preflight.tsv"

if [[ "$HAS_CONVENTIONAL" == "true" ]]; then
  git log --format='FIXCOMMIT|%aI|%s' --name-only --no-merges $SINCE_FLAG | awk '
  BEGIN { OFS="\t" }

  /^FIXCOMMIT\|/ {
    split($0, parts, "|")
    date = parts[2]
    subject = ""
    for (i = 3; i <= length(parts); i++) {
      if (i > 3) subject = subject "|"
      subject = subject parts[i]
    }
    is_fix = (tolower(subject) ~ /^fix[(:!]/)
    next
  }

  /^$/ { next }

  {
    if (is_fix) {
      print $0, substr(date, 1, 10), subject
    }
  }
  ' > "$OUTPUT_DIR/fix_commits_raw.tsv"

  sort -t$'\t' -k1,1 -k2,2 "$OUTPUT_DIR/fix_commits_raw.tsv" | awk -F'\t' '
  BEGIN { OFS="\t" }

  function days_between(d1, d2) {
    split(d1, a, "-")
    split(d2, b, "-")
    epoch1 = (a[1] * 365 + a[2] * 30 + a[3])
    epoch2 = (b[1] * 365 + b[2] * 30 + b[3])
    diff = epoch2 - epoch1
    if (diff < 0) diff = -diff
    return diff
  }

  {
    file = $1
    date = $2

    if (file == prev_file && days_between(prev_date, date) <= 7) {
      fix_count[file]++
    }
    prev_file = file
    prev_date = date
  }

  END {
    for (f in fix_count) {
      print f, fix_count[f]
    }
  }
  ' > "$OUTPUT_DIR/fix_after_fix.tsv"

  rm -f "$OUTPUT_DIR/fix_commits_raw.tsv"
fi

# ---------------------------------------------------------------------------
# Cross-directory commits — no author needed
# ---------------------------------------------------------------------------
git log --format='COMMIT_HASH:%H' --name-only --no-merges $SINCE_FLAG | awk '
BEGIN { OFS="\t" }

/^COMMIT_HASH:/ {
  if (hash != "" && dir_count > 1) {
    cross_dir_commits++
  }
  hash = substr($0, 13)
  delete dirs
  dir_count = 0
  next
}

/^$/ { next }

{
  idx = index($0, "/")
  if (idx > 0) {
    dir = substr($0, 1, idx - 1)
  } else {
    dir = "(root)"
  }
  if (!(dir in dirs)) {
    dirs[dir] = 1
    dir_count++
  }
}

END {
  if (hash != "" && dir_count > 1) {
    cross_dir_commits++
  }
  print cross_dir_commits + 0
}
' > "$OUTPUT_DIR/cross_dir_commits.tsv"

# ---------------------------------------------------------------------------
# Revert detection
# ---------------------------------------------------------------------------
awk -F'\t' '
BEGIN { OFS="\t" }
{
  subject = $3
  if (subject ~ /^Revert /) {
    date = $2
    month = substr(date, 1, 7)
    print date, month, subject
  }
}
' "$OUTPUT_DIR/subjects.tsv" > "$OUTPUT_DIR/reverts.tsv"

# ---------------------------------------------------------------------------
# Done — print output directory
# ---------------------------------------------------------------------------
echo "$OUTPUT_DIR"
