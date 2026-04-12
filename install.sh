#!/usr/bin/env bash
# archeia install — symlink domain skills into ~/.claude/skills/
# and personal subagents into ~/.claude/agents/
set -e

ARCHEIA_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- skills ---
SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_DIR"

for skill in "$ARCHEIA_DIR"/skills/*/*/SKILL.md; do
  [ -e "$skill" ] || continue
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  ln -sfn "$dir" "$SKILLS_DIR/$name"
  echo "  linked skill $name"
done

# --- agents ---
AGENTS_DIR="$HOME/.claude/agents"
mkdir -p "$AGENTS_DIR"

for agent in "$ARCHEIA_DIR"/agents/*.md; do
  [ -e "$agent" ] || continue
  name="$(basename "$agent")"
  # Skip README.md — it's documentation for humans, not a subagent definition
  [ "$name" = "README.md" ] && continue
  ln -sfn "$agent" "$AGENTS_DIR/$name"
  echo "  linked agent $name"
done
