#!/usr/bin/env python3
"""Package every skill under .apm/skills/ as a self-contained archive.

Each skill becomes dist/<name>.skill (and an identical dist/<name>.zip) whose
single top-level entry is the skill folder, which is the layout Claude expects:

    git.skill
    └── git/
        ├── SKILL.md
        └── references/

Archives are byte-for-byte reproducible: entries are sorted and stamped with a
fixed timestamp, so an unchanged skill always produces the same bytes.

Run it locally the same way CI does:

    pip install pyyaml
    python3 .github/scripts/pack_skills.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".apm" / "skills"
DIST_DIR = REPO_ROOT / "dist"
APM_MANIFEST = REPO_ROOT / "apm.yml"

# Fixed zip timestamp (the epoch zip itself supports) keeps builds reproducible.
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

EXCLUDED_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}

# Descriptions are long; the release table gets a trimmed version.
TABLE_DESCRIPTION_LIMIT = 160


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)


def read_frontmatter(skill_md: Path) -> dict:
    """Parse the YAML frontmatter block at the top of a SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("no YAML frontmatter block (expected a leading '---' fence)")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return data


def normalise(text: str) -> str:
    return " ".join(str(text).split())


def iter_skill_files(skill_dir: Path) -> list[Path]:
    """Every packable file in a skill, sorted for reproducibility."""
    files = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        if any(part in EXCLUDED_NAMES for part in path.relative_to(skill_dir).parts):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(skill_dir).as_posix())


def add_skill_to_zip(archive: zipfile.ZipFile, skill_dir: Path) -> None:
    """Write one skill folder into an open archive, under its own name."""
    for path in iter_skill_files(skill_dir):
        arcname = f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}"
        info = zipfile.ZipInfo(arcname, date_time=FIXED_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        # Preserve the executable bit for scripts, otherwise plain 0644.
        mode = 0o755 if path.stat().st_mode & 0o100 else 0o644
        info.external_attr = mode << 16
        archive.writestr(info, path.read_bytes())


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def discover_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        (d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()),
        key=lambda d: d.name,
    )


def validate(skill_dir: Path) -> tuple[dict | None, list[str]]:
    """Return (frontmatter, errors) for one skill."""
    errors: list[str] = []
    try:
        meta = read_frontmatter(skill_dir / "SKILL.md")
    except (ValueError, yaml.YAMLError) as exc:
        return None, [f"{skill_dir.name}: {exc}"]

    name = meta.get("name")
    if not name:
        errors.append(f"{skill_dir.name}: frontmatter is missing 'name'")
    elif normalise(name) != skill_dir.name:
        errors.append(
            f"{skill_dir.name}: frontmatter name '{name}' does not match its directory"
        )

    description = meta.get("description")
    if not description or not normalise(description):
        errors.append(f"{skill_dir.name}: frontmatter is missing 'description'")

    return meta, errors


def package_name() -> str:
    try:
        manifest = yaml.safe_load(APM_MANIFEST.read_text(encoding="utf-8")) or {}
    except OSError:
        return REPO_ROOT.name
    return manifest.get("name") or REPO_ROOT.name


def package_version() -> str | None:
    try:
        manifest = yaml.safe_load(APM_MANIFEST.read_text(encoding="utf-8")) or {}
    except OSError:
        return None
    version = manifest.get("version")
    return str(version) if version is not None else None


def render_release_notes(entries: list[dict], repo: str, tag: str) -> str:
    base = f"https://github.com/{repo}/releases/download/{tag}"
    lines = [
        f"{len(entries)} skills, each packaged as a standalone archive.",
        "",
        "Download one, unzip it into `~/.claude/skills/` (or your project's",
        "`.claude/skills/`), and it is ready to use. The `.zip` copy is byte-identical",
        "and exists because claude.ai's uploader only accepts that extension.",
        "",
        "| Skill | Description | Download |",
        "|---|---|---|",
    ]
    for entry in entries:
        description = entry["description"]
        if len(description) > TABLE_DESCRIPTION_LIMIT:
            description = description[:TABLE_DESCRIPTION_LIMIT].rstrip() + "…"
        description = description.replace("|", "\\|")
        name = entry["name"]
        lines.append(
            f"| `{name}` | {description} "
            f"| [`{name}.skill`]({base}/{name}.skill) · [`.zip`]({base}/{name}.zip) |"
        )
    lines += [
        "",
        f"Every skill in one archive: [`{package_name()}-all-skills.zip`]"
        f"({base}/{package_name()}-all-skills.zip)",
        "",
        "`SHA256SUMS` and `skills.json` are attached for verification and scripting.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect-version",
        help="Fail unless apm.yml's version matches this (accepts a leading 'v').",
    )
    parser.add_argument(
        "--repo",
        default="mmsge/evnar",
        help="owner/repo used to build download links in the release notes.",
    )
    parser.add_argument(
        "--tag",
        default="latest",
        help="Release tag used to build download links in the release notes.",
    )
    args = parser.parse_args()

    if args.expect_version:
        expected = args.expect_version.lstrip("v")
        actual = package_version()
        if actual != expected:
            fail(
                f"tag version '{expected}' does not match apm.yml version "
                f"'{actual}'. Bump apm.yml, or retag."
            )
            return 1
        print(f"version check: apm.yml is {actual}, matching the tag")

    skills = discover_skills()
    if not skills:
        fail(f"no skills found under {SKILLS_DIR.relative_to(REPO_ROOT)}")
        return 1

    errors: list[str] = []
    validated: list[tuple[Path, dict]] = []
    for skill_dir in skills:
        meta, skill_errors = validate(skill_dir)
        errors.extend(skill_errors)
        if meta is not None and not skill_errors:
            validated.append((skill_dir, meta))

    if errors:
        fail(f"{len(errors)} skill(s) failed validation:")
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
        return 1

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    entries: list[dict] = []
    for skill_dir, meta in validated:
        name = skill_dir.name
        skill_path = DIST_DIR / f"{name}.skill"
        with zipfile.ZipFile(skill_path, "w", zipfile.ZIP_DEFLATED) as archive:
            add_skill_to_zip(archive, skill_dir)
        shutil.copy2(skill_path, DIST_DIR / f"{name}.zip")

        entries.append(
            {
                "name": name,
                "description": normalise(meta["description"]),
                "file": f"{name}.skill",
                "size": skill_path.stat().st_size,
                "sha256": sha256_of(skill_path),
                "files": len(iter_skill_files(skill_dir)),
            }
        )
        print(f"packed {name}.skill ({entries[-1]['files']} files, {entries[-1]['size']} bytes)")

    bundle_path = DIST_DIR / f"{package_name()}-all-skills.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for skill_dir, _ in validated:
            add_skill_to_zip(archive, skill_dir)
    print(f"packed {bundle_path.name} ({len(validated)} skills)")

    (DIST_DIR / "skills.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    checksum_lines = []
    for path in sorted(DIST_DIR.iterdir()):
        if path.suffix in {".skill", ".zip"}:
            checksum_lines.append(f"{sha256_of(path)}  {path.name}")
    (DIST_DIR / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    (DIST_DIR / "RELEASE_NOTES.md").write_text(
        render_release_notes(entries, args.repo, args.tag), encoding="utf-8"
    )

    print(f"\n{len(entries)} skills written to {DIST_DIR.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
