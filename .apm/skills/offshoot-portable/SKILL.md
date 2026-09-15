---
name: offshoot-portable
version: 1.0.0
description: The cross-client build of `offshoot`. Use this one on Codex, GitHub Copilot or ChatGPT, or anywhere `spawn_task` is absent. Turn a one-line request into a well-scoped brief and hand it to an independent agent session, running elsewhere in its own isolated environment. Use whenever the user wants work done somewhere other than here — "offshoot", "spin this off", "spin off a session", "fire off a session", "start a new session for X", "background task", "delegate this", "do that again for X", "queue that up", "hand this to another agent", "not now, but later" — and use it proactively before calling any delegation tool by hand, because an unbriefed offshoot arrives with no memory of this conversation and improvises past the constraints that matter.
---

# Offshoot (portable)

Spin a piece of work out of this session into its own. The spawned session starts in a
fresh environment with **no memory of this conversation** — not the constraints you were
given, not what is half-finished on the branch, not the reason a particular command is
off-limits. Everything it needs has to be in the brief, which is why passing the user's
sentence through unchanged fails: it reads as a task with no edges, and an agent with no
edges finds a helpful workaround.

Read `references/brief-anatomy.md` before writing the brief. It carries the checklist and
a worked example; this file is only the workflow.

## 0. Find the handoff first

Which delegation mechanism exists here decides whether there is a session to brief at all,
so settle it before spending tool calls. Take the first of these that is actually in your
toolset, and do not go looking for a substitute if none is.

| Client | Mechanism | Shape |
|---|---|---|
| Claude Code | `spawn_task` (often `mcp__ccd_session__spawn_task`) | Offers a chip that starts a fresh session in an isolated git worktree. |
| Copilot, GitHub MCP server, remote | `create_pull_request_with_copilot` | Takes `problem_statement`, which is the brief. Starts a coding agent run in an ephemeral environment on its own branch, ending in one draft PR. |
| Copilot, GitHub MCP server, local | `assign_copilot_to_issue` | Same agent, entered through an issue. Put the brief in `custom_instructions`. |
| Copilot in VS Code | `#copilotCodingAgent` | Same agent again. It scopes locally first, then asks the user to confirm before it hands off. |
| Codex, ChatGPT, anything else | none | Go to **Hand-over mode** at step 4. |

Two rules about that table.

**A subagent is not an offshoot.** Claude Code's `Task`, Codex's `subagents`, and any
"spawn N agents and summarise" facility all return into this conversation. A session that
runs on its own is a different thing, and quietly swapping one for the other is not what
was asked for. If the only delegation tool you have reports back, you are in hand-over
mode, not in a lesser version of spawn mode.

**A scheduled task is not an offshoot either.** A timer that reruns a prompt later is not
an independent session in an isolated environment, whatever it is called.

## 1. Gather, before asking anything

Spend the tool calls here rather than in questions. Most of what the brief needs is on
disk or in this conversation already.

- `git rev-parse --show-toplevel`, then read that repo's `AGENTS.md`, `CLAUDE.md` or
  whatever it keeps its house rules in, in full. Pull out the handful of invariants that
  bear on **this** task, not all of them. A brief that quotes three relevant rules gets
  read; one that restates the whole file gets skimmed.
- `git status` and `git log --oneline -5`. Uncommitted work, the current branch and any
  open pull request are things the offshoot must not disturb, and it cannot see them.
- Scan this conversation for constraints you were given that still apply over there:
  a resource that must be left alone, a rate limit, a permission cache, a mailbox someone
  else is using. These are the most valuable thing you have, because they exist nowhere
  on disk.
- If the repo records decisions somewhere, a `docs/decision-records/` tree, ADRs, a
  design-notes folder, read its index for the house shape and the current count. If it
  records them nowhere, note that too: it changes where a proposal has to land.

If you have no shell here, or the sandbox refuses to start one, say so plainly and build
the brief from the conversation and whatever you can read. A brief written blind is worth
less, and the user should know which parts you could not check rather than find out later.

## 2. Ask only what changes the brief

Use one interactive question round, or none. Where the client has a structured question
tool, use it; where it does not, ask in plain text and keep it to one turn. Usually two
questions are enough:

- **What must the new session not touch?** Offer the candidates you found, the in-flight
  branch, a live system, an external service with a cost or a cooldown, rather than an
  open-ended prompt.
- **Build it, or investigate and report?** These produce genuinely different briefs, and
  guessing wrong wastes a whole session.

Anything you can settle by reading, settle by reading. Questions whose answers would not
change a line of the brief are friction.

## 3. Write the brief

Follow `references/brief-anatomy.md`. The short version, in order: hard constraints with
a reason attached to each; the isolation boundary named as concrete commands, modules and
hostnames; where credentials live and how to load them without printing them; the specific
repo rules quoted, plus a pointer to the file they came from; a stopping point, if the work
is really a decision rather than a task; the local mechanics that bite; and what good looks
like at the end.

Never put a secret in the brief. It is a message that gets stored and displayed; tell the
offshoot where the credential lives instead.

Write the brief the same way whichever mechanism you found at step 0. The only thing that
changes below is where it goes.

## 4. Hand it over, once

One handoff per invocation. If the description covers two separable pieces of work, name
the split and ask which one to spin off rather than firing two. How the work divides is
the user's call, not yours.

### Spawn mode, Claude Code

One `spawn_task` call.

- `title` — imperative, under 60 characters, starts with a verb.
- `tldr` — one or two plain sentences. Lead with what you noticed here that prompted it,
  then what the new session will do. No file paths, no code; this is the chip label's
  subtitle, read at a glance.
- `prompt` — the brief. Long is fine. It is the whole inheritance.
- `cwd` — omit unless the work plainly belongs in a different repository on this machine.

### Spawn mode, GitHub Copilot

One tool call, whichever of the three you found.

- `create_pull_request_with_copilot`: `problem_statement` is the brief, whole and
  unabridged. `title` follows the same rule as above. Pass `owner` and `repo` from
  `git remote -v` rather than guessing, and `base_ref` if the work should start from
  something other than the default branch.
- `assign_copilot_to_issue`: the brief goes in `custom_instructions`. Use this only when
  an issue already exists and genuinely describes the work; do not open one purely as a
  container.
- `#copilotCodingAgent`: pass the brief as the task description. The agent will scope
  locally and then ask the user to confirm, so tell the user that the confirmation is
  coming rather than leaving them to discover it.

Two things to put in the brief here that the Claude Code version does not need. The agent
gets a hard 59-minute ceiling, so if the work cannot plausibly land inside that, say so
before handing it over rather than after. And it ends in exactly one draft pull request,
so "what good looks like" should describe that PR rather than a file left on a branch.

### Hand-over mode, no delegation tool

Say in one sentence that this client has no way to start an independent session, then give
the brief anyway, in a fenced block the user can copy whole. Do not soften this into a
half-measure and do not start the work yourself; the point was to move it elsewhere.

Where the user can plausibly run it, name the surface rather than waving at one:

- **Codex app**: a new thread creates its own disposable worktree, so the brief pasted
  into a fresh thread gets the isolation it assumes.
- **Codex CLI**: there is no worktree flag, so the brief needs `git worktree add` in front
  of it. Say that.
- **Codex cloud, or ChatGPT**: a new cloud task, started by the user from that surface.

## Then report back

The title, the constraints you encoded, anything you assumed, and which mechanism you
used. If you were in hand-over mode, say that plainly. Do not also start doing the work
yourself.
