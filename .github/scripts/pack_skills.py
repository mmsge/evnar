#!/usr/bin/env python3
"""Package every skill under .apm/skills/ as a self-contained, versioned archive.

Each skill is released on its own, under its own tag, so a single skill can be
shared as a link to a release page rather than a link to a raw file:

    https://github.com/mmsge/evnar/releases/tag/offshoot-v1.0.0

The version comes from the `version:` field in the skill's SKILL.md
frontmatter. Bump it when you change the skill and CI cuts the release; leave
it alone and CI leaves the existing release alone. Versions are semver:

    Z  a fix or a wording change
    Y  a new, backwards-compatible capability
    X  a change that breaks how the skill is used

Output layout:

    dist/
      offshoot/
        offshoot.skill        the archive, one top-level folder named for the skill
        offshoot.zip          byte-identical copy; claude.ai only accepts .zip
        RELEASE_NOTES.md      body for this skill's release
        SHA256SUMS
      evnar-all-skills.zip    every skill, for the repo-wide vX.Y.Z release
      skills.json             name, version, tag, size and digest for every skill
      SHA256SUMS
      RELEASE_NOTES.md        body for the repo-wide vX.Y.Z release

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

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

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

    version = meta.get("version")
    if version is None:
        errors.append(
            f"{skill_dir.name}: frontmatter is missing 'version' "
            f"(add e.g. 'version: 1.0.0' under 'name')"
        )
    elif not SEMVER.match(str(version)):
        errors.append(
            f"{skill_dir.name}: version '{version}' is not semver X.Y.Z"
        )

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


def trimmed(description: str) -> str:
    if len(description) > TABLE_DESCRIPTION_LIMIT:
        description = description[:TABLE_DESCRIPTION_LIMIT].rstrip() + "…"
    return description.replace("|", "\\|")


def render_skill_notes(entry: dict, repo: str) -> str:
    """Body for one skill's own release page."""
    name, tag = entry["name"], entry["tag"]
    base = f"https://github.com/{repo}/releases/download/{tag}"
    return "\n".join(
        [
            f"`{name}` {entry['version']}, packaged as a standalone skill.",
            "",
            entry["description"],
            "",
            "## Install",
            "",
            "```bash",
            f"curl -LO {base}/{name}.skill",
            f"unzip {name}.skill -d ~/.claude/skills/",
            "```",
            "",
            f"That gives `~/.claude/skills/{name}/SKILL.md`. Use a project's",
            "`.claude/skills/` instead to scope it to one repository.",
            "",
            f"For claude.ai, upload [`{name}.zip`]({base}/{name}.zip) instead. It is",
            "byte-identical and exists only because that uploader rejects any other",
            "extension.",
            "",
            "## Verify",
            "",
            "```",
            f"{entry['sha256']}  {name}.skill",
            "```",
            "",
            f"{entry['files']} files, {entry['size']} bytes. Built reproducibly from "
            f"[`.apm/skills/{name}/`](https://github.com/{repo}/tree/hovud/.apm/skills/{name}).",
        ]
    ) + "\n"


def render_package_notes(entries: list[dict], repo: str, tag: str) -> str:
    """Body for the repo-wide vX.Y.Z release carrying the all-skills bundle."""
    base = f"https://github.com/{repo}/releases/download/{tag}"
    lines = [
        f"Snapshot of all {len(entries)} skills at {package_name()} {tag}.",
        "",
        f"Every skill in one archive: [`{package_name()}-all-skills.zip`]"
        f"({base}/{package_name()}-all-skills.zip)",
        "",
        "Skills are also released individually, and an individual release is the",
        "better thing to link to when you want to share just one.",
        "",
        "| Skill | Version | Description |",
        "|---|---|---|",
    ]
    for entry in entries:
        lines.append(
            f"| [`{entry['name']}`](https://github.com/{repo}/releases/tag/{entry['tag']}) "
            f"| {entry['version']} | {trimmed(entry['description'])} |"
        )
    lines += [
        "",
        "`SHA256SUMS` and `skills.json` are attached for verification and scripting.",
    ]
    return "\n".join(lines) + "\n"


def render_summary(entries: list[dict]) -> str:
    """Job-summary table for the Actions run."""
    lines = ["## Packed skills", "", "| Skill | Version | Tag | SHA256 |", "|---|---|---|---|"]
    for entry in entries:
        lines.append(
            f"| `{entry['name']}` | {entry['version']} "
            f"| `{entry['tag']}` | `{entry['sha256'][:16]}…` |"
        )
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
        default=None,
        help="Repo-wide release tag used in the bundle's release notes.",
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
        version = str(meta["version"])
        skill_out = DIST_DIR / name
        skill_out.mkdir()

        skill_path = skill_out / f"{name}.skill"
        with zipfile.ZipFile(skill_path, "w", zipfile.ZIP_DEFLATED) as archive:
            add_skill_to_zip(archive, skill_dir)
        shutil.copy2(skill_path, skill_out / f"{name}.zip")

        entry = {
            "name": name,
            "version": version,
            "tag": f"{name}-v{version}",
            "description": normalise(meta["description"]),
            "file": f"{name}.skill",
            "size": skill_path.stat().st_size,
            "sha256": sha256_of(skill_path),
            "files": len(iter_skill_files(skill_dir)),
        }
        entries.append(entry)

        (skill_out / "RELEASE_NOTES.md").write_text(
            render_skill_notes(entry, args.repo), encoding="utf-8"
        )
        (skill_out / "SHA256SUMS").write_text(
            f"{entry['sha256']}  {name}.skill\n{entry['sha256']}  {name}.zip\n",
            encoding="utf-8",
        )
        print(f"packed {entry['tag']} ({entry['files']} files, {entry['size']} bytes)")

    bundle_path = DIST_DIR / f"{package_name()}-all-skills.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for skill_dir, _ in validated:
            add_skill_to_zip(archive, skill_dir)
    print(f"packed {bundle_path.name} ({len(validated)} skills)")

    (DIST_DIR / "skills.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    checksum_lines = [f"{sha256_of(bundle_path)}  {bundle_path.name}"]
    for entry in entries:
        checksum_lines.append(f"{entry['sha256']}  {entry['name']}.skill")
    (DIST_DIR / "SHA256SUMS").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    package_tag = args.tag or f"v{package_version()}"
    (DIST_DIR / "RELEASE_NOTES.md").write_text(
        render_package_notes(entries, args.repo, package_tag), encoding="utf-8"
    )

    (DIST_DIR / "SUMMARY.md").write_text(render_summary(entries), encoding="utf-8")

    print(f"\n{len(entries)} skills written to {DIST_DIR.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
