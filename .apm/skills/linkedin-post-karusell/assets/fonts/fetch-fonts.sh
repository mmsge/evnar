#!/usr/bin/env bash
# Fetch the three Lato weights the carousel uses into this directory.
# Lato is SIL OFL 1.1 (free to bundle). Requires network access.
set -euo pipefail
cd "$(dirname "$0")"

BASE="https://github.com/google/fonts/raw/main/ofl/lato"
for f in Lato-Black.ttf Lato-Bold.ttf Lato-Regular.ttf; do
  echo "Hentar $f ..."
  curl -fsSL "$BASE/$f" -o "$f"
done

echo "Ferdig. Skrifter i $(pwd):"
ls -1 Lato-*.ttf
