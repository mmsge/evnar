# GitHub Workflows

## Checking `gh` availability

First check if `gh` is installed and authenticated:

```bash
gh auth status 2>/dev/null || echo "gh not available"
```

If `gh` is not installed, prompt the user:
> "You don't have the GitHub CLI (`gh`) installed. I recommend installing it from https://cli.github.com
> — it lets me manage PRs, issues, and Actions directly from your terminal without spending extra
> tokens on MCP server calls. For now I'll fall back to the GitHub MCP server."

If `gh` is available, prefer it for all remote operations.

---

## Pull requests

### Create a PR

```bash
gh pr create \
  --title "feat(scope): short description" \
  --body "$(cat <<'EOF'
## Summary
- What changed and why

## Test plan
- [ ] How to verify

🤖 Generated with Claude via Cowork
EOF
)"
```

Always confirm the target branch before creating. Default is usually `main` or `hovud`.

### View PR status

```bash
gh pr status           # PRs related to current branch
gh pr list             # all open PRs in the repo
gh pr view <number>    # detailed view of a specific PR
```

### Review a PR

```bash
gh pr checkout <number>          # check out the PR branch locally
git diff origin/main...HEAD      # see exactly what changed
gh pr review <number> --comment  # leave a comment
gh pr review <number> --approve  # approve
gh pr review <number> --request-changes  # request changes
```

### Merge a PR

```bash
gh pr merge <number> --squash    # squash merge (most common)
gh pr merge <number> --merge     # regular merge commit
gh pr merge <number> --rebase    # rebase merge
```

---

## Issues

```bash
gh issue list                    # open issues
gh issue view <number>           # read an issue
gh issue create --title "" --body ""  # new issue
gh issue close <number>          # close
```

---

## GitHub Actions (CI)

### Check workflow status

```bash
gh run list --limit 10           # recent workflow runs
gh run view <run-id>             # status of a specific run
gh run view <run-id> --log       # full logs
gh run watch                     # stream the current run live
```

### Trigger a workflow manually

```bash
gh workflow run <workflow-name>
```

---

## When to use the GitHub MCP server instead of `gh`

Use the GitHub MCP server (`mcp__GitHub_MCP_Server__*`) only when:
- You need to read or post inline PR review comments (thread-level)
- You need structured data from the API that `gh` doesn't expose cleanly
- `gh` is not installed and the operation is complex

For simple status checks, PR creation, and issue management, `gh` CLI is always preferred.
