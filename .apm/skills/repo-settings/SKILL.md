---
name: repo-settings
description: Apply standard GitHub repository settings (squash-only merging, PR housekeeping, feature toggles) to a repo from the bundled settings.json. Use when creating or setting up a new repository, when asked to standardise or fix repo settings, or right after gh repo create.
---

# repo-settings

GitHub does not inherit repository settings from templates, so this skill applies
the canonical settings bundled in `settings.json` to whatever repo is being worked
on. It is fully standalone: the data lives in this folder and nothing needs to be
generated or fetched first.

## Requirements

- `gh` CLI, authenticated as someone with admin access on the target repo
- `jq`

In environments without `gh` (for example Claude Code web/remote sessions), report
that the settings cannot be applied from here and stop — do not try to reproduce
the API calls another way.

## Flow

1. Resolve the target repo from the current directory:
   `gh repo view --json nameWithOwner -q .nameWithOwner`
2. Dry-run and show the diff: `./apply.sh <owner/repo>`
3. If there are changes, confirm with the user, then run
   `./apply.sh <owner/repo> --apply`

`apply.sh` sends exactly the keys present in `settings.json` as one PATCH, and the
PATCH is idempotent — safe to run repeatedly.

## The policy in settings.json

- Squash-only merging (merge commits and rebase merging disabled); the squash
  commit defaults to the PR title + PR description
- Auto-delete head branches after merge, allow auto-merge, always suggest
  updating PR branches
- Features: issues and projects on, wiki and discussions off

`settings.json` is literally the request body for GitHub's
`PATCH /repos/{owner}/{repo}` endpoint — edit it, or add any other field that
endpoint accepts, to change the policy.

## Deliberately out of scope

- Default branch name — inherited natively for new repos via
  https://github.com/settings/repositories ("Repository default branch")
- Security & analysis, rulesets/branch protection, Actions defaults — not part of
  the per-repo routine this skill automates

## Install / share

This folder is self-contained and tied to no particular repository. To have the
skill trigger in any project, copy it to the personal skills directory:

    cp -r repo-settings ~/.claude/skills/

To share it, send someone the folder; they only need to review `settings.json`.
