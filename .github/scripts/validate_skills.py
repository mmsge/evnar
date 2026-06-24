#!/usr/bin/env python3
"""Validate APM skills against the documented agent-skills rules.

Errors (fail CI):
  - Each entry in .apm/skills/ is a directory containing SKILL.md (exact case).
  - SKILL.md starts with a YAML frontmatter block (--- ... ---) parsing to a mapping.
  - Non-empty `name` and `description`.
  - `name` == folder name; kebab-case [a-z0-9] with single hyphens; 1..64 chars.
  - `description` <= 1024 chars.
  - No SKILL.md nested deeper than .apm/skills/<name>/SKILL.md.
Warnings (do not fail):
  - Frontmatter keys beyond name/description.
  - Subdirs other than scripts/references/assets/examples.
  - Body > 500 lines.
Plus a light apm.yml sanity check (valid YAML mapping with a name).
Ref: https://microsoft.github.io/apm/producer/author-primitives/skills
"""
import re
import sys
from pathlib import Path

import yaml

SKILLS_DIR = Path(".apm/skills")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX, DESC_MAX, BODY_MAX_LINES = 64, 1024, 500
ALLOWED_SUBDIRS = {"scripts", "references", "assets", "examples"}
errors, warnings = [], []


def split_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def validate_skill(skill_dir):
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        wrong = [p.name for p in skill_dir.iterdir()
                 if p.is_file() and p.name.lower() == "skill.md"]
        errors.append(f"{skill_dir}: skill file must be named exactly 'SKILL.md'"
                      f" (found {wrong[0]})" if wrong else f"{skill_dir}: missing SKILL.md")
        return
    fm, body = split_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm is None:
        errors.append(f"{skill_md}: missing/unterminated YAML frontmatter (--- ... ---)")
        return
    try:
        data = yaml.safe_load(fm)
    except yaml.YAMLError as e:
        errors.append(f"{skill_md}: frontmatter not valid YAML: {e}")
        return
    if not isinstance(data, dict):
        errors.append(f"{skill_md}: frontmatter must be a YAML mapping")
        return
    nm = data.get("name")
    if not nm or not isinstance(nm, str):
        errors.append(f"{skill_md}: missing required non-empty 'name'")
    else:
        if nm != name:
            errors.append(f"{skill_md}: name '{nm}' must equal folder name '{name}'")
        if not NAME_RE.match(nm):
            errors.append(f"{skill_md}: name '{nm}' must be kebab-case "
                          "(a-z, 0-9, single hyphens; no leading/trailing/double hyphen)")
        if len(nm) > NAME_MAX:
            errors.append(f"{skill_md}: name '{nm}' exceeds {NAME_MAX} chars")
    desc = data.get("description")
    if not desc or not isinstance(desc, str):
        errors.append(f"{skill_md}: missing required non-empty 'description'")
    elif len(desc) > DESC_MAX:
        errors.append(f"{skill_md}: description is {len(desc)} chars (max {DESC_MAX})")
    extra = set(data) - {"name", "description"}
    if extra:
        warnings.append(f"{skill_md}: non-standard frontmatter keys: {sorted(extra)}")
    for sub in skill_dir.iterdir():
        if sub.is_dir() and sub.name not in ALLOWED_SUBDIRS:
            warnings.append(f"{skill_dir}: non-standard subdir '{sub.name}/' "
                            f"(expected {sorted(ALLOWED_SUBDIRS)})")
    if len(body.splitlines()) > BODY_MAX_LINES:
        warnings.append(f"{skill_md}: body is {len(body.splitlines())} lines "
                        f"(convention <= {BODY_MAX_LINES})")


def main():
    if not SKILLS_DIR.is_dir():
        print(f"No {SKILLS_DIR}/ directory; nothing to validate.")
        return 0
    entries = sorted(p for p in SKILLS_DIR.iterdir() if not p.name.startswith("."))
    for f in (p for p in entries if p.is_file()):
        errors.append(f"{f}: unexpected file directly under {SKILLS_DIR}/ "
                      "(skills must be folders)")
    skill_dirs = [p for p in entries if p.is_dir()]
    for d in skill_dirs:
        validate_skill(d)
    for sk in SKILLS_DIR.rglob("SKILL.md"):
        if sk.parent.parent != SKILLS_DIR:
            errors.append(f"{sk}: SKILL.md must be at {SKILLS_DIR}/<name>/SKILL.md")
    apm_yml = Path("apm.yml")
    if apm_yml.is_file():
        try:
            meta = yaml.safe_load(apm_yml.read_text(encoding="utf-8"))
            if not isinstance(meta, dict) or not meta.get("name"):
                errors.append("apm.yml: must be a YAML mapping with a 'name'")
        except yaml.YAMLError as e:
            errors.append(f"apm.yml: invalid YAML: {e}")
    else:
        warnings.append("apm.yml not found at repo root")
    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")
    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s), "
              f"{len(skill_dirs)} skill(s).")
        return 1
    print(f"\nOK: {len(skill_dirs)} skill(s) valid, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
