# What makes an offshoot brief good

The brief is the spawned session's entire inheritance. It has no memory of the
conversation that produced it, no sight of the working tree it came from, and no way to
ask a follow-up question before it starts. Everything below exists because an agent
missing that piece did something reasonable and wrong.

Write the sections in this order. The order is itself load-bearing: constraints read
before the task are constraints; constraints read after it are footnotes.

The examples use an invented repository — a billing sync in `Acme-Co/invoicer` — purely to
keep them concrete. Substitute the real commands, modules and hostnames of the repo you
are actually spinning work out of.

---

## 1. Hard constraints first, each with its reason

An agent told only "do not use X" treats it as an obstacle and routes around it — calling
the same API through a different module, or trying a variant of the command to see whether
that one is allowed. An agent told **why** understands what it is protecting, and protects
it in situations you did not anticipate.

Weak: *Do not use the billing tooling.*

Strong: *Do not touch the billing API or any customer account. Separate work is waiting on
a rate-limit window that reopens only after 30 minutes with no calls from that API key,
and one call from this session costs Markus another half hour.*

The second version survives a case the first never covered, because the agent now knows
what "touching" means and what it costs.

## 2. Name the isolation boundary concretely

"Stay away from the billing code" is not actionable — the agent has to guess where the
edges are, and it guesses generously. Enumerate: the commands, the modules, the hostnames,
the accounts. Four concrete lines beat one careful sentence.

> No `billsync` invocations, no imports from `cli/billing.py` or `app/invoicer/billing/`,
> no `make sync-once`, no requests to `api.billing.example.com`, and nothing involving the
> live or sandbox account ids.

Say what **is** safe, too. An agent that cannot verify anything writes untested code, so
if `make check` is offline and safe, say that in the same breath — otherwise the list of
prohibitions reads as "do not run anything".

## 3. Credentials: where they live, and how to use them unread

The offshoot will need configuration and must not print it into a transcript. Name the
file, say it is gitignored, and give it the loading idiom rather than a `cat`: source the
file into the environment with `set -a` / `set +a` around it, so the values are available
to commands without ever being displayed. Then add the two rules that go with it — never
commit the file, and never echo a variable read from it.

## 4. Quote the repo rules that bear on this task

Tell it to read `CLAUDE.md` **and** quote the three or four rules that actually apply. A
pointer alone gets skimmed under time pressure; a quoted rule sitting in the prompt is
still there when the agent is deciding what to do at step nine.

Choose by relevance, not by importance. For work touching persistence, quote the personal
data rule and the secrets rule. For work adding a tool, quote the one-language rule. Three
that bite are worth more than all eight recited.

## 5. Apply the authority rule

If the work touches a dependency or vendor, personal data or what gets persisted, auth or
secrets, a contract with another system, or deployment topology, the offshoot may not
simply implement it. Say so explicitly, and say what to do instead:

> This touches deployment topology, so it is a consult-level decision under the authority
> rule in `CLAUDE.md`. Write the decision record at `status: proposed`, with
> `deciders: Markus`, and stop there. Do not implement past the record and do not mark it
> accepted — Markus decides, and a proposed record is the correct artefact for a decision
> that has not been taken yet.

Without this, a capable agent delivers a finished, well-tested implementation of a decision
that was never his to skip.

## 6. The local mechanics that bite

These cost a session an hour each and are invisible from inside a fresh worktree. The
specifics differ per repo; what generalises is that you have to write them down.

- **`gh` and a second organisation.** When `gh` is logged in as several accounts, the
  active one often cannot resolve `Acme-Co/...`, so `gh pr create` fails with "Could not
  resolve to a Repository" — which looks like a missing repository or a permissions
  problem and is neither. Run `gh auth switch --hostname github.com --user work-markus`
  first, pass `--repo Acme-Co/invoicer` explicitly, and switch back to `personal-markus`
  afterwards so the environment is left as it was found.
- **Counts stated as prose go stale.** Adding a decision record falsifies the record
  counts written out in `CLAUDE.md` and in `docs/decision-records/index.md`. Fix them in
  the same change, along with any cross-reference the change made wrong — Markus wants
  that repo-wide rather than left for later.
- **`make check` must pass** before anything is handed back, and the test count should not
  drop.

## 7. End with what good looks like

Name the deliverable concretely — a file at a path, a passing check, an opened pull
request — so "done" is observable rather than a judgement call. Then give explicit
permission to come back with less:

> If the investigation shows this is not worth doing, or that it needs a decision from
> Markus first, a short honest document saying so is a better outcome than speculative
> code. Say what you found, what you did not verify, and what you would need in order to
> finish.

An agent that believes it must produce code produces code. That permission is what buys an
honest answer instead.

---

## Worked example

A brief spun off from a session that was mid-way through unrelated work. Note that the
prohibitions come before the task, that each carries a reason, and that the last paragraph
lets the offshoot decline to build.

````
Add a secret scanner to this repository's CI, or report why it should not be added.

## Do not touch these, and why

Do not touch the billing API or any customer account: no `billsync` commands, no imports
from `cli/billing.py` or `app/invoicer/billing/`, no `make sync-once`, no requests to
`api.billing.example.com`, and nothing involving either the live or the sandbox account
ids. Separate work is waiting on a rate-limit window that reopens only after 30 minutes
with no calls from that API key, and a single call from this session costs Markus another
half hour.

`make check` is safe — it is entirely offline, and it is how you verify your work.

Leave the branch `claude/sync-once-reads-env-f7082b` and its open pull request alone. You
are in your own worktree, so this mostly means: do not rebase, do not force-push, and do
not amend commits you did not write.

## Context

Read `CLAUDE.md` at the repo root in full before starting. Three of its rules bear
directly on this task:

- "**No secrets.** Configuration comes from the environment." The tracked example
  environment file may hold non-secret values — the service account name, the application
  and tenant ids — but never a client secret, certificate, connection string with an
  account key, or token.
- "**No personal data in this repository, in any form.** Not in examples, fixtures,
  documentation, commit messages or issues." Any test data you write for the scanner must
  be obviously invented.
- "**The language is Python, and there is exactly one.**" A scanner that drags in a second
  runtime needs a decision record, not a pull request.

`CLAUDE.md` already names a secret scanner in CI as "the next check worth adding", so this
is wanted in principle. What is open is which one, and at what cost.

Configuration lives in the gitignored environment file at the repo root. You almost
certainly do not need it, but if you do: source it into the environment rather than reading
it out, and never echo a value from it into the transcript.

## Authority

Adding a scanner adds a dependency, and wiring it into CI touches deployment topology.
Both are consult-level under the authority rule in `CLAUDE.md`. So: write the decision
record at `status: proposed` with `deciders: Markus`, name the alternatives you considered
and why each lost, and stop there. Do not mark it accepted, and do not read a proposed
record as permission to merge the implementation under it.

Use `make adr SLUG=...` to scaffold it. Adding a record falsifies the record counts stated
in prose in `CLAUDE.md` and in `docs/decision-records/index.md` — update both, and check
that every relative link still resolves.

## Mechanics

`gh` cannot resolve `Acme-Co/...` under its default account. Before any `gh` command:
`gh auth switch --hostname github.com --user work-markus`, pass `--repo Acme-Co/invoicer`
explicitly, and switch back to `personal-markus` when you are done.

`make check` must pass, with no drop in test count.

## What good looks like

A `proposed` decision record naming a specific scanner and the trade-off it carries, the
index and the prose counts updated, `make check` passing, and a pull request opened for
Markus to read.

If the honest conclusion is that no scanner fits — the candidates are too noisy, or the
guard tests already in `tests/guards/` cover the realistic cases — then say that in the
record instead, and open the pull request with the record alone. A short document arguing
against the work is a better outcome than a scanner nobody will keep.
````

---

## Before you emit the call

- Could an agent with no other context follow this and stay inside the boundary?
- Does every prohibition carry a reason?
- Is the boundary made of names — commands, modules, hosts — rather than adjectives?
- Does it say what is safe to run, not only what is forbidden?
- Does the task trip the authority rule, and if so does the brief stop at `proposed`?
- Is "done" observable, and is declining to build explicitly allowed?
- Is there any secret in the prompt text? There must be none.
