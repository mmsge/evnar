---
name: offshoot
description: Turn a one-line request into a well-scoped background task via the spawn_task tool, which offers Markus a chip that starts a fresh session in an isolated worktree. Use whenever he wants work done somewhere other than here — "offshoot", "spin this off", "spin off a session", "fire off a session", "start a new session for X", "background task", "do that again for X", "queue that up", "hand this to another agent", "not now, but later" — and use it proactively before calling spawn_task by hand, because an unbriefed offshoot arrives with no memory of this conversation and improvises past the constraints that matter.
---

# Offshoot

Spin a piece of work out of this session into its own. The spawned session starts in a
fresh worktree with **no memory of this conversation** — not the constraints you were
given, not what is half-finished on the branch, not the reason a particular command is
off-limits. Everything it needs has to be in the brief, which is why passing Markus's
sentence through unchanged fails: it reads as a task with no edges, and an agent with no
edges finds a helpful workaround.

Read `references/brief-anatomy.md` before writing the brief. It carries the checklist and
a worked example; this file is only the workflow.

## 1. Gather, before asking anything

Spend the tool calls here rather than in questions. Most of what the brief needs is on
disk or in this conversation already.

- `git rev-parse --show-toplevel`, then read that repo's `CLAUDE.md` in full. Pull out the
  handful of invariants that bear on **this** task — not all of them. A brief that quotes
  three relevant rules gets read; one that restates the whole file gets skimmed.
- `git status` and `git log --oneline -5`. Uncommitted work, the current branch and any
  open pull request are things the offshoot must not disturb, and it cannot see them.
- Scan this conversation for constraints you were given that still apply over there —
  a resource that must be left alone, a rate limit, a permission cache, a mailbox someone
  else is using. These are the most valuable thing you have, because they exist nowhere
  on disk.
- If the work might need a decision record, read `docs/decision-records/index.md` for the
  house shape and the current count.

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
repo rules quoted, plus a pointer to `CLAUDE.md`; the authority rule, if the work touches
anything consult-level; the local mechanics that bite; and what good looks like at the end.

## 4. Emit exactly one spawn_task call

One `mcp__ccd_session__spawn_task` call per invocation. If the description covers two
separable pieces of work, name the split and ask which one to spin off rather than firing
two chips — how the work divides is Markus's call, not yours.

- `title` — imperative, under 60 characters, starts with a verb.
- `tldr` — one or two plain sentences. Lead with what you noticed here that prompted it,
  then what the new session will do. No file paths, no code; this is the chip label's
  subtitle, read at a glance.
- `prompt` — the brief. Long is fine. It is the whole inheritance.
- `cwd` — omit unless the work plainly belongs in a different repository on this machine.

Never put a secret in the prompt. It is a message that gets stored and displayed; tell the
offshoot where the credential lives instead.

Then report back: the title, the constraints you encoded, and anything you assumed. Do not
also start doing the work yourself — the point was to move it elsewhere.
