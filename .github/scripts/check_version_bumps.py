#!/usr/bin/env python3
"""Fail a pull request that edits a skill without bumping its version.

Releases are cut from the `version:` field in SKILL.md, so a change merged
without a bump is a change that never reaches anyone. This catches that while
the pull request is still open.

    python3 .github/scripts/check_version_bumps.py --base origin/hovud
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pack_skills import REPO_ROOT, SKILLS_DIR, read_frontmatter  # noqa: E402

SKILLS_PREFIX = SKILLS_DIR.relative_to(REPO_ROOT).as_posix()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout


def changed_skills(base: str) -> set[str]:
    """Skill names touched between base and the working tree."""
    names = set()
    for line in git("diff", "--name-only", f"{base}...HEAD").splitlines():
        parts = line.split("/")
        # .apm/skills/<name>/...
        if len(parts) >= 4 and "/".join(parts[:2]) == SKILLS_PREFIX:
            names.add(parts[2])
    return names


MISSING = object()  # the skill itself did not exist at that ref


def version_at(ref: str, name: str):
    """A skill's declared version at a git ref.

    Returns MISSING if the skill did not exist there, None if it existed but
    declared no version, otherwise the version string. The three cases need
    different answers, so they stay distinguishable.
    """
    path = f"{SKILLS_PREFIX}/{name}/SKILL.md"
    try:
        text = git("show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return MISSING
    tmp = Path(REPO_ROOT, ".git", "check-version-tmp.md")
    tmp.write_text(text, encoding="utf-8")
    try:
        version = read_frontmatter(tmp).get("version")
    except Exception:
        return None
    finally:
        tmp.unlink(missing_ok=True)
    return str(version) if version is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/hovud", help="branch to compare against")
    args = parser.parse_args()

    touched = changed_skills(args.base)
    if not touched:
        print("no skills changed; nothing to check")
        return 0

    problems = []
    for name in sorted(touched):
        before = version_at(args.base, name)
        after = version_at("HEAD", name)
        if after is MISSING:
            print(f"{name}: removed")
            continue
        if after is None:
            problems.append(
                f"{name}: no 'version' in frontmatter. Add one, e.g. 'version: 1.0.0'."
            )
            continue
        if before is MISSING:
            print(f"{name}: new at {after}")
            continue
        if before is None:
            print(f"{name}: newly versioned at {after}")
            continue
        if before == after:
            problems.append(
                f"{name}: changed but still at version {after}. Bump it in "
                f"{SKILLS_PREFIX}/{name}/SKILL.md, or the change never gets released."
            )
        else:
            print(f"{name}: {before} -> {after}")

    if problems:
        print(f"\nerror: {len(problems)} skill(s) changed without a version bump:", file=sys.stderr)
        for message in problems:
            print(f"  - {message}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
