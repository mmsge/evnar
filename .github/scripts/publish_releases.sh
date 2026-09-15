#!/usr/bin/env bash
#
# Publish one GitHub release per skill, tagged <skill>-v<version>.
#
# The version in a skill's SKILL.md frontmatter is the whole trigger: if no
# release carries that tag yet, this creates it; if one already does, the skill
# is left alone. So a release happens exactly when you bump a version, and
# re-running the workflow never rewrites a published archive.
#
# Expects dist/ to have been built by pack_skills.py, and GH_TOKEN in the
# environment.

set -euo pipefail

dist="${DIST_DIR:-dist}"
target="${GITHUB_SHA:-}"
manifest="$dist/skills.json"

if [[ ! -f "$manifest" ]]; then
  echo "error: $manifest not found; run pack_skills.py first" >&2
  exit 1
fi

created=0
skipped=0

# One tab-separated line per skill: tag, name, version.
while IFS=$'\t' read -r tag name version; do
  if gh release view "$tag" >/dev/null 2>&1; then
    echo "skip   $tag (already released)"
    skipped=$((skipped + 1))
    continue
  fi

  echo "create $tag"
  gh release create "$tag" \
    --title "$name $version" \
    --notes-file "$dist/$name/RELEASE_NOTES.md" \
    ${target:+--target "$target"} \
    "$dist/$name/$name.skill" \
    "$dist/$name/$name.zip" \
    "$dist/$name/SHA256SUMS"
  created=$((created + 1))
done < <(python3 -c '
import json, sys
for e in json.load(open(sys.argv[1])):
    print(f"{e[\"tag\"]}\t{e[\"name\"]}\t{e[\"version\"]}")
' "$manifest")

echo
echo "$created release(s) created, $skipped already present"
