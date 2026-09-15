# Installing offshoot-portable

One skill, four clients. The `SKILL.md` and `references/` directory are identical
everywhere; only the install path changes.

This is the cross-client sibling of [`offshoot`](../.apm/skills/offshoot/SKILL.md),
which stays Claude Code only. Installing this package with APM deploys both, so on
Claude Code you will have the two side by side.

## Claude Code

| Scope | Path |
|---|---|
| Project | `.claude/skills/offshoot-portable/` |
| Personal | `~/.claude/skills/offshoot-portable/` |

Triggers automatically from the `description`. Runs in spawn mode via `spawn_task`.

## GitHub Copilot

| Scope | Path |
|---|---|
| Repo | `.github/skills/offshoot-portable/` |
| Repo, shared | `.agents/skills/offshoot-portable/` |
| Personal | `~/.copilot/skills/offshoot-portable/` |

Copilot also reads `.claude/skills/` directly, so a repo that already has the Claude
copy may need nothing further. Triggers automatically from the `description`.

Spawn mode needs one of:

- the GitHub MCP server **remote** endpoint, for `create_pull_request_with_copilot`
- the GitHub MCP server **local** build, for `assign_copilot_to_issue` (needs the `repo`
  OAuth scope)
- VS Code with the GitHub Pull Requests extension, for `#copilotCodingAgent`

Without one of those it falls back to hand-over mode, which still works.

## Codex

| Scope | Path |
|---|---|
| Repo | `.agents/skills/offshoot-portable/` |
| Personal | `~/.agents/skills/offshoot-portable/` |
| Admin | `/etc/codex/skills/offshoot-portable/` |

Triggers automatically, or explicitly with `$offshoot-portable`. Add
`allow_implicit_invocation: false` to the frontmatter if you want it manual only.

Codex has no model-callable way to start an independent session, so this always runs in
hand-over mode. `subagents` are deliberately not used: they report back into the same
conversation, which is a different thing. That is a correct outcome, not a failure.

Note that step 1 is entirely shell calls. If the Codex sandbox cannot start a shell, the
skill will say so and write the brief from conversation context alone.

## ChatGPT

Install through the skills editor or by uploading this directory. Business, Enterprise,
Healthcare and Edu plans only at time of writing; not Plus or Free.

Always hand-over mode. Codex sits in a separate view with separate history and there is no
documented handoff from a chat conversation, so the brief goes to the user to paste.

## Turning hand-over mode into spawn mode on Codex

Not built here, and worth knowing the shape before anyone tries. A small stdio MCP server
registered with `codex mcp add` could expose a `spawn_task` tool that does
`git worktree add` and then launches a detached `codex exec` inside it. `codex cloud exec`
is the other route, but it needs an environment id provisioned by hand, since there is no
scriptable way to create or resolve one yet.
