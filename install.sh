#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APM_BIN="${APM_BIN:-apm}"
DEFAULT_TARGETS="${APM_TARGETS:-all,agent-skills}"

HAS_TARGET=false
APM_ARGS=()

usage() {
  cat <<'USAGE'
Usage: ./install.sh [options]

Runs:
  apm install --target all,agent-skills

Options:
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

if ! command -v "$APM_BIN" >/dev/null 2>&1; then
  echo "error: apm is required. Install it from https://microsoft.github.io/apm/ and retry." >&2
  exit 127
fi

cd "$ROOT_DIR"
if $HAS_TARGET; then
  "$APM_BIN" install "${APM_ARGS[@]}"
else
  "$APM_BIN" install --target "$DEFAULT_TARGETS" "${APM_ARGS[@]}"
fi

echo ""
echo "APM command complete."
