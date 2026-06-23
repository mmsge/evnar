#!/usr/bin/env bash
# Compare a repo's settings against settings.json; with --apply, update the repo.
# Usage: apply.sh <owner/repo> [--apply]
set -euo pipefail

usage() { echo "usage: apply.sh <owner/repo> [--apply]" >&2; exit 2; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
settings="$here/settings.json"

target=""
mode="dry-run"
for arg in "$@"; do
  case "$arg" in
    --apply) mode="apply" ;;
    -*) usage ;;
    *) [ -z "$target" ] || usage; target="$arg" ;;
  esac
done
[ -n "$target" ] || usage

for dep in gh jq; do
  command -v "$dep" >/dev/null || { echo "error: $dep is required" >&2; exit 1; }
done
gh auth status >/dev/null || { echo "error: gh is not authenticated (run: gh auth login)" >&2; exit 1; }

desired="$(jq -c '.' "$settings")"
current="$(gh api "repos/$target")"

changes=0
while IFS= read -r key; do
  want="$(jq -r --arg k "$key" '.[$k]' <<<"$desired")"
  have="$(jq -r --arg k "$key" '.[$k]' <<<"$current")"
  if [ "$want" != "$have" ]; then
    printf '  %-30s %s -> %s\n' "$key" "$have" "$want"
    changes=$((changes + 1))
  fi
done < <(jq -r 'keys[]' <<<"$desired")

if [ "$changes" -eq 0 ]; then
  echo "$target already matches settings.json — nothing to change."
  exit 0
fi

if [ "$mode" = "apply" ]; then
  printf '%s' "$desired" | gh api -X PATCH "repos/$target" --input - >/dev/null
  echo "Applied $changes setting(s) to $target."
else
  echo "Dry run: $changes setting(s) differ on $target. Re-run with --apply to update."
fi
