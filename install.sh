#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/skills" && pwd)"
TARGET_DIR="${HOME}/.claude/skills"
FORCE=false

for arg in "$@"; do
  [[ "$arg" == "--force" ]] && FORCE=true
done

mkdir -p "$TARGET_DIR"

installed=0
skipped=0

for skill_path in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_path")"
  target="$TARGET_DIR/$skill_name"

  if [[ -e "$target" || -L "$target" ]]; then
    if $FORCE; then
      rm -rf "$target"
    else
      echo "  skip  $skill_name (already exists — use --force to overwrite)"
      skipped=$((skipped + 1))
      continue
    fi
  fi

  ln -s "$skill_path" "$target"
  echo "  ok    $skill_name"
  installed=$((installed + 1))
done

echo ""
echo "$installed installed, $skipped skipped."
echo "Restart Claude Code for changes to take effect."
