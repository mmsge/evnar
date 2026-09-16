---
name: offshoot
version: 1.1.0
description: Turn a one-line request into a well-scoped background task and hand it to a session of its own, through the `spawn_task` tool in local Claude Code or the `create_session` tool on claude.ai/code. Use whenever Markus wants work done somewhere other than here, in words like "offshoot", "spin this off", "spin off a session", "fire off a session", "start a new session for X", "background task", "do that again for X", "queue that up", "hand this to another agent", "not now, but later". Use it proactively before calling either tool by hand, because an unbriefed offshoot arrives with no memory of this conversation and improvises past the constraints that matter.
---

# Offshoot

Spin a piece of work out of this session into its own. The spawned session starts in a
fresh checkout with **no memory of this conversation** — not the constraints you were
given, not what is half-finished on the branch, not the reason a particular command is
off-limits. Everything it needs has to be in the brief, which is why passing Markus's
sentence through unchanged fails: it reads as a task with no edges, and an agent with no
edges finds a helpful workaround.

Read `references/brief-anatomy.md` before writing the brief. It carries the checklist and
a worked example; this file is only the workflow.

## 0. Find the handoff first

There are two, and which one you have changes what the offshoot can see, so settle it
before spending tool calls. Take whichever is actually in your toolset.

| Where you are | Tool | What it does |
|---|---|---|
| Claude Code on this machine | `spawn_task`, often `mcp__ccd_session__spawn_task` | Offers Markus a chip. Clicking it starts a fresh session in an isolated git worktree, on this machine, with the rest of the disk still reachable. |
| claude.ai/code, or anywhere the Claude Code Remote MCP server is mounted | `create_session`, often `mcp__Claude_Code_Remote__create_session` | Starts the session immediately, no chip. It runs in its own remote container, cloned fresh from the git remote, and nothing of this machine is reachable from it. |

That last difference is the one that bites. A local worktree is a clean checkout beside a
machine that still has the gitignored environment file, the logged-in `gh`, the local
database. A remote container has only what is pushed to the remote plus what the
environment supplies, so a brief that says "the credentials are in the env file at the
repo root" sends it looking for a file that is not there. `references/brief-anatomy.md`
section 8 carries the three parts of the brief that change.

Two rules about the table.

**A subagent is not an offshoot.** The `Agent` tool, `Task`, and any "spawn N agents and
summarise" facility all return into this conversation. A session that runs on its own is a
different thing, and quietly swapping one for the other is not what was asked for.

**A scheduled task is not an offshoot either.** A trigger that reruns a prompt later is not
an independent session in an isolated environment, whatever it is called.

If neither tool is present, say so in one sentence rather than reaching for the nearest
substitute, then write the brief anyway and give it to Markus in a fenced block he can
copy whole. The brief is most of the value; the chip is not.

## 1. Gather, before asking anything

Spend the tool calls here rather than in questions. Most of what the brief needs is on
disk or in this conversation already.

- `git rev-parse --show-toplevel`, then read that repo's `CLAUDE.md`, `AGENTS.md` or
  whatever it keeps its house rules in, in full. Pull out the handful of invariants that
  bear on **this** task — not all of them. A brief that quotes three relevant rules gets
  read; one that restates the whole file gets skimmed.
- `git status` and `git log --oneline -5`. Uncommitted work, the current branch and any
  open pull request are things the offshoot must not disturb, and it cannot see them.
- Heading for `create_session`, also run `git remote -v` and
  `git log --oneline origin/<branch>..HEAD`. The offshoot clones from the remote, so
  commits that exist only here are invisible to it. If the work builds on any of them,
  push first and name the revision in the brief; if you cannot push, say which parts of
  the brief the offshoot will not be able to see.
- Scan this conversation for constraints you were given that still apply over there —
  a resource that must be left alone, a rate limit, a permission cache, a mailbox someone
  else is using. These are the most valuable thing you have, because they exist nowhere
  on disk.
- If the repo records decisions somewhere — a `docs/decision-records/` tree, ADRs, a
  design-notes folder — read its index for the house shape and the current count. If it
  records them nowhere, note that too: it changes where a proposal has to land.

## 2. Ask only what changes the brief

Use one `AskUserQuestion` round, or none. Usually two questions are enough:

- **What must the new session not touch?** Offer the candidates you found — the in-flight
  branch, a live system, an external service with a cost or a cooldown — rather than an
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
like at the end. Section 8 revises three of those for a remote container.

Never put a secret in the brief. It is a message that gets stored and displayed; tell the
offshoot where the credential lives instead.

## 4. Emit exactly one call

One call per invocation, whichever tool you found. If the description covers two separable
pieces of work, name the split and ask which one to spin off rather than firing two — how
the work divides is Markus's call, not yours.

### Local Claude Code: `spawn_task`

- `title` — imperative, under 60 characters, starts with a verb.
- `tldr` — one or two plain sentences. Lead with what you noticed here that prompted it,
  then what the new session will do. No file paths, no code; this is the chip label's
  subtitle, read at a glance.
- `prompt` — the brief. Long is fine. It is the whole inheritance.
- `cwd` — omit unless the work plainly belongs in a different repository on this machine.

### claude.ai/code: `create_session`

This one starts the session the moment you call it. There is no chip between you and a
running agent, so the brief has to be finished before the call rather than after it, and
the report back has to tell Markus that something is already running.

- `prompt` — the brief. Long is fine. It is the whole inheritance.
- `title` — imperative, under 60 characters, starts with a verb. There is no `tldr` field
  here, so open the brief with the sentence you would have put in one: what you noticed
  that prompted this, then what the new session will do.
- `environment_id` — omit. It inherits this session's environment, which is the one whose
  network policy and environment variables the brief assumes. Never invent an id;
  `list_environments` is where real ones come from.
- `source_url` and `source_revision` — omit for the repository you are already in. Give
  them when the work belongs to another repository, and confirm that repository is in this
  session's scope first, with `list_repos` and then `add_repo`, rather than discovering it
  is not from inside the new session. This pair is the replacement for `cwd`: there is no
  local disk over there to point at.
- `model` — omit to inherit this session's, or name a smaller one when the work is
  mechanical rather than a judgement call. Choose it deliberately and say which you chose.
- `permission_mode` — omit to inherit. Never pass `plan`: it makes the session propose a
  plan and then block on a human approval in the web UI, and nobody is watching it.
- `outcome_branch` — only when the branch name matters to something outside the session,
  such as a pull request that already exists. Otherwise let it derive one.
- `tags` — worth setting when you spin off more than one piece of work, so they can be
  listed together afterwards.

## Then report back

The title, the constraints you encoded, anything you assumed, and which mechanism you
used. Do not also start doing the work yourself — the point was to move it elsewhere.

After a `create_session` call, give Markus the session id along with the title, say
plainly that it is already running rather than waiting on a click, and name the controls:
`interrupt_session` stops it mid-turn, `get_session` reports where it got to, and
`archive_session` retires it once the work has landed.
