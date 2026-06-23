---
name: git
description: >
  Expert git workflow assistant covering everything from local commits and branch management to
  pull requests, code review, and CI/Actions checks. Use this skill whenever the user is working
  in a git project — regardless of whether they say "git", "GitHub", "Forgejo", "PR", "branch",
  "commit", "push", "merge", "diff", "rebase", or "CI". Also trigger for phrases like "make a
  pull request", "check the build", "what branch am I on", "push my changes", "review this PR",
  "open an issue", or "create a branch". Always use this skill for git work — do NOT improvise
  a workflow without it.
---

# Git Skill

This skill guides Claude through git workflows in a way that is fast, safe, and frugal with
tokens. The core principle: **use the cheapest tool that can answer the question**. Local git
commands are almost free. CLI tools like `gh` or `tea` are inexpensive. MCP servers cost tokens
and should be a last resort.

---

## Step 0 — Orientation (always do this first)

Before touching anything, run these two commands:

```bash
git remote get-url origin 2>/dev/null || echo "(no remote)"
git branch --show-current
```

This tells you:
1. **Which platform** the project lives on (GitHub vs Forgejo vs other)
2. **Which branch** is currently checked out

If the remote URL contains `github.com` → this is a **GitHub** project.  
If not, check if it looks like a self-hosted instance (e.g. `codeberg.org`, `gitea.io`, a
private domain). If unsure, ask: *"Is this project hosted on GitHub or Forgejo?"*

---

## Step 1 — Branch safety

**Never make changes on a default branch.** Default branches are typically named `main`, `master`,
or `hovud`. If the current branch is one of these, stop immediately and create a new branch:

```bash
git checkout -b <descriptive-branch-name>
```

Choose a branch name that reflects the task (e.g. `fix/login-bug`, `feat/dark-mode`,
`docs/update-readme`). Use kebab-case.

If the user hasn't described what they're doing yet, ask before creating the branch so the name
is meaningful.

---

## Tool hierarchy

Always use the cheapest tool that can do the job. Work your way down this list only when the
tier above can't help:

| Tier | Tools | Use for |
|------|-------|---------|
| 1 — Local | `git` CLI | Status, log, diff, branch, stash, rebase, local history |
| 2 — CLI | `gh` (GitHub) or `tea` (Forgejo) | Creating/viewing PRs, issues, releases, workflow runs |
| 3 — MCP | GitHub MCP Server | PR review threads, Actions logs, complex queries that CLI can't express |
| 4 — API | Forgejo REST API via curl/fetch | Forgejo operations when `tea` isn't installed |

**Rule:** If you catch yourself reaching for an MCP tool to answer something `git log` or `git
diff` could answer, step back.

MCP tools are appropriate for:
- Reading or posting PR review comments
- Checking GitHub Actions / Forgejo Actions workflow status
- Fetching issue details or creating issues
- Anything that requires authenticating to the remote as a user

---

## GitHub workflows

Read `references/github.md` when working on a GitHub project.

---

## Forgejo workflows

Read `references/forgejo.md` when working on a Forgejo project.

---

## Common operations quick reference

### Committing

```bash
git status                        # see what's changed
git diff                          # review unstaged changes
git diff --staged                 # review staged changes
git add <files>                   # stage specific files (avoid `git add .`)
git commit -m "type(scope): msg"  # commit
```

Follow Conventional Commits format: `type(scope): short description`. Types: `feat`, `fix`,
`docs`, `refactor`, `test`, `chore`, `ci`.

### Branch management

```bash
git branch -a                     # list all branches
git checkout -b <name>            # create and switch
git checkout <name>               # switch to existing
git branch -d <name>              # delete local branch (after merge)
git push origin <name>            # push branch to remote
git push origin --delete <name>   # delete remote branch
```

### Viewing history and diffs

```bash
git log --oneline -20             # recent commits
git log --oneline --graph         # branch graph
git diff <branch>                 # compare to another branch
git diff HEAD~3                   # last 3 commits
git show <sha>                    # inspect a specific commit
```

### Stashing

```bash
git stash                         # save uncommitted work temporarily
git stash pop                     # restore it
git stash list                    # see all stashes
```

### Rebasing / keeping up to date

```bash
git fetch origin
git rebase origin/main            # rebase current branch onto main
git rebase -i HEAD~N              # interactive rebase last N commits
```

Prefer rebase over merge for keeping feature branches clean, unless the project convention
dictates otherwise.

---

## Guardrails

- **Never force-push to a default branch.** Warn the user loudly if they ask.
- **Never skip hooks** (`--no-verify`) unless the user explicitly asks and understands why.
- **Never commit secrets** — if a file looks like it might contain credentials (`.env`,
  `*_key.*`, `credentials.*`), flag it before staging.
- **Prefer new commits over amend** unless the user explicitly says to amend.
- **Always quote paths with spaces** in shell commands.
