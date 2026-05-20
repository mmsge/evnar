#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${ROOT_DIR}/.apm/skills"
TARGET_DIR="${HOME}/.claude/skills"
APM_BIN="${APM_BIN:-apm}"
DEFAULT_TARGETS="${APM_TARGETS:-all,agent-skills}"

LEGACY_ONLY=false
FORCE=false
HAS_TARGET=false
APM_ARGS=()

usage() {
  cat <<'USAGE'
Usage: ./install.sh [options]

Runs APM when available:
  apm install --target all,agent-skills

Options:
  --legacy-claude   Skip APM and symlink skills into ~/.claude/skills.
  --force           Overwrite existing legacy Claude skill symlinks.
  --target, -t      Pass a custom APM target value.
  --help            Show this help.

All other options are forwarded to `apm install`.
USAGE
}

while [[ $# -gt 0 ]]; do
  arg="$1"
  case "$arg" in
    --help|-h)
      usage
      exit 0
      ;;
    --legacy-claude)
      LEGACY_ONLY=true
      shift
      ;;
    --force)
      FORCE=true
      APM_ARGS+=("$arg")
      shift
      ;;
    --target|-t)
      HAS_TARGET=true
      APM_ARGS+=("$arg")
      shift
      if [[ $# -eq 0 ]]; then
        echo "error: $arg requires a value" >&2
        exit 2
      fi
      APM_ARGS+=("$1")
      shift
      ;;
    --target=*)
      HAS_TARGET=true
      APM_ARGS+=("$arg")
      shift
      ;;
    *)
      APM_ARGS+=("$arg")
      shift
      ;;
  esac
done

legacy_claude_install() {
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
        echo "  skip  $skill_name (already exists -- use --force to overwrite)"
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
}

if ! $LEGACY_ONLY && command -v "$APM_BIN" >/dev/null 2>&1; then
  cd "$ROOT_DIR"
  if $HAS_TARGET; then
    "$APM_BIN" install "${APM_ARGS[@]}"
  else
    "$APM_BIN" install --target "$DEFAULT_TARGETS" "${APM_ARGS[@]}"
  fi
  echo ""
  echo "APM install complete."
  exit 0
fi

if ! $LEGACY_ONLY; then
  echo "apm not found on PATH; falling back to legacy Claude skill symlinks."
  echo "Install APM later to deploy prompts, instructions, agents, hooks, and MCP."
  echo ""
fi

legacy_claude_install
