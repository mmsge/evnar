---
name: project-review
description: >
  Analyze a software project and produce a ranked Markdown report of suggested
  improvements — both optimizations of existing features and entirely new ones.
  Each suggestion includes a rationale, an effort estimate, and a ready-to-use
  prompt a coding LLM can act on immediately.

  Use this skill whenever the user asks to "review my project", "suggest
  improvements", "what could be better about this codebase", "give me ideas for
  new features", "audit my code", or anything that implies stepping back and
  thinking critically about a project as a whole. Also trigger when the user
  says things like "roast my project", "what am I missing", or "how can I level
  this up".
---

# Project Review Skill

Your job is to act as a thoughtful senior engineer reviewing a codebase. You're
not looking for bugs (unless they're glaring) — you're looking for the kinds of
improvements a good code review or architecture session would surface: things
that would meaningfully raise quality, developer experience, performance, or
user value.

## Phase 1 — Understand the Project

Before suggesting anything, spend time actually understanding what the project
is and what it's trying to do. Rush this and your suggestions will be generic
and useless.

**Start with orientation:**
- Look for a README, package.json, pyproject.toml, Cargo.toml, go.mod, or
  similar manifest file. This tells you the project's purpose and tech stack.
- Scan the top-level directory structure to understand how it's organized.
- Identify the entry point(s) — main file, index, routes, etc.

**Then go deeper:**
- Read the key source files — focus on the ones with the most logic, not
  boilerplate or generated code.
- Look at config files (CI, linting, testing, build tools) to understand the
  development workflow.
- Check for tests — their presence, coverage, and quality say a lot.
- Look for a CHANGELOG or git log if available to understand recent focus areas.

Don't try to read every file. Use judgment about what matters. If the project
is large, prioritize breadth over depth — skim widely, then read the critical
parts carefully.

## Phase 2 — Identify Improvements

Think across these dimensions as you read:

**Code quality & maintainability**
- Is the code organized in a way that will scale? Are there god objects, deep
  nesting, or tangled dependencies?
- Is there duplication that should be abstracted?
- Are there obvious performance issues (N+1 queries, synchronous I/O where
  async would help, missing caching)?

**Developer experience**
- How easy is it to set up and run locally?
- Is there a test suite, and is it meaningful?
- Are there missing scripts, poor error messages, or confusing config?

**User/product value**
- Are there features that are clearly half-done or that a similar project would
  typically have?
- Are there UX or API friction points that a user would notice?

**Reliability & production-readiness**
- Error handling — is it present and meaningful, or missing and silent?
- Logging, monitoring, health checks?
- Security considerations (hardcoded secrets, SQL injection surface, missing
  auth)?

**Ecosystem & tooling**
- Outdated dependencies with known better alternatives?
- Missing tooling that the ecosystem has converged on (formatters, linters,
  type checking)?

Generate **5–10 suggestions** unless the project is tiny (then 3–5 is fine).
Prioritize ruthlessly — the top items should be things that genuinely matter,
not nitpicks dressed up as important.

## Phase 3 — Write the Report

Output a single Markdown document. Use this exact structure:

---

```markdown
# Project Review: [Project Name]

> [One sentence describing what the project is and what it does.]

---

## Summary

[2–4 sentences. What's the overall health of the project? What are the 1–2
biggest themes that came up across your review?]

---

## Suggested Improvements

Ranked from most to least recommended.

---

### 1. [Short imperative title, e.g. "Add integration tests for the auth module"]

**Why this matters:** [1–3 sentences on the problem and its impact. Be
specific — reference actual files or patterns you saw.]

**Effort:** Small | Medium | Large

**Implementation prompt:**

> [A concise, self-contained prompt (3–6 sentences) that a coding LLM like
> Claude or Copilot could act on directly. It should identify what to do, where
> to do it, and any constraints or context the implementer needs. Write it in
> second person, as if speaking to the LLM: "Refactor the `UserService` class
> in `src/services/user.ts` to..."]

---

### 2. [Title]

...

---

## What's Working Well

[2–4 bullet points. Acknowledge the genuine strengths — this makes the
critique more credible and helps the developer know what not to change.]
```

---

## Effort Scale

Use consistent definitions so the estimates are meaningful:

- **Small** — A focused change, likely one file or a few related files. A
  developer familiar with the codebase could finish it in under half a day.
- **Medium** — Touches multiple areas or requires some design decisions. Could
  take a day or two.
- **Large** — Significant rework or a meaningful new feature. Multiple days to
  a week or more.

## A Note on Tone

Be direct. The point of this report is to be genuinely useful, not to flatter.
That said, assume the developer cares about their work — frame things as
opportunities rather than failures. "The test coverage is low" is a fact;
"Adding tests here would make it much safer to refactor the core logic later"
is a reason to act.

The implementation prompts in particular should be optimistic and
action-oriented — the person reading them wants to ship improvements, so make
it as easy as possible to hand one off to a coding assistant and get moving.
