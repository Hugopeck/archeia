#!/usr/bin/env bash
# archeia install — symlink all domain skills into ~/.claude/skills/
set -e

ARCHEIA_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_DIR"

for skill in "$ARCHEIA_DIR"/skills/*/*/SKILL.md; do
  [ -e "$skill" ] || continue
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  ln -sfn "$dir" "$SKILLS_DIR/$name"
  echo "  linked $name"
done
