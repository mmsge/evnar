# Forgejo Workflows

## Checking `tea` availability

First check if `tea` (the Gitea/Forgejo CLI) is installed:

```bash
tea --version 2>/dev/null || echo "tea not available"
```

If `tea` is not installed, suggest installing it:
> "`tea` is the official CLI for Forgejo/Gitea. Install it to manage PRs and issues without burning
> tokens on API calls:
>
> **macOS:** `brew install tea`  
> **Linux:** Download from https://gitea.com/gitea/tea/releases or `go install gitea.io/gitea/tea@latest`
>
> For now, I'll use the Forgejo REST API directly."

### Configuring `tea` (first time only)

```bash
tea login add --name my-forgejo \
  --url https://your-forgejo-instance.example.com \
  --token <your-api-token>
```

Generate a token at: `https://<instance>/user/settings/applications`

---

## Pull requests with `tea`

```bash
tea pr list                          # open PRs
tea pr create --title "" --description ""  # new PR
tea pr view <number>                 # read a PR
tea pr merge <number>                # merge
tea pr close <number>                # close without merging
```

## Issues with `tea`

```bash
tea issue list                       # open issues
tea issue create --title "" --description ""
tea issue close <number>
```

## CI / Forgejo Actions

Forgejo Actions uses the same YAML format as GitHub Actions. Check run status:

```bash
# tea doesn't yet fully support Actions; use the API instead:
curl -s -H "Authorization: token <TOKEN>" \
  "https://<instance>/api/v1/repos/<owner>/<repo>/actions/runs?limit=10" \
  | jq '.workflow_runs[] | {id, name, status, conclusion}'
```

Or open the Forgejo web UI directly — Actions tab in the repo.

---

## Fallback: Forgejo REST API

When `tea` isn't installed or doesn't cover the operation, use the Forgejo REST API. The base
URL pattern is: `https://<instance>/api/v1/`

Get your API token from the instance's user settings, or read it from an env var:

```bash
FORGEJO_TOKEN=$(cat ~/.config/forgejo/token 2>/dev/null || echo "$FORGEJO_TOKEN")
FORGEJO_URL="https://your-instance.example.com"
REPO="owner/repo-name"
```

### Common API calls

```bash
# List open PRs
curl -s -H "Authorization: token $FORGEJO_TOKEN" \
  "$FORGEJO_URL/api/v1/repos/$REPO/pulls?state=open" \
  | jq '.[] | {number, title, user: .user.login, head: .head.label}'

# Create a PR
curl -s -X POST -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  "$FORGEJO_URL/api/v1/repos/$REPO/pulls" \
  -d '{"title":"feat: my change","head":"my-branch","base":"main","body":"Description here"}'

# List open issues
curl -s -H "Authorization: token $FORGEJO_TOKEN" \
  "$FORGEJO_URL/api/v1/repos/$REPO/issues?type=issues&state=open" \
  | jq '.[] | {number, title}'

# Create an issue
curl -s -X POST -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  "$FORGEJO_URL/api/v1/repos/$REPO/issues" \
  -d '{"title":"Bug: something","body":"Steps to reproduce..."}'
```

### Finding the instance URL

Extract it from the git remote:

```bash
git remote get-url origin
# e.g. https://git.example.com/markus/my-project.git
# → FORGEJO_URL = https://git.example.com
# → REPO = markus/my-project
```

Or for SSH remotes (`git@git.example.com:markus/my-project.git`):

```bash
git remote get-url origin | sed 's|git@\(.*\):\(.*\)\.git|https://\1/\2|'
```

---

## When to use the Forgejo API vs `tea`

- **`tea` installed** → use it for everything interactive (PRs, issues, releases)
- **`tea` not installed** → use `curl` + Forgejo REST API
- **Always use local `git`** for branch/commit/diff work regardless
