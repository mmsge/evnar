---
name: linkedin-post-timing
description: >
  Decide WHEN to publish Markus's LinkedIn posts — recommend a specific time slot for a finished post, design a recurring posting cadence, and slot a backlog of generated post ideas into a sensible schedule. This is the companion to the linkedin-post-karusell skill: that one makes the post, this one decides when it goes live. Use this skill whenever Markus asks about LinkedIn timing, scheduling, cadence, or frequency. Triggers include: "when should I post this", "what's the best time to post", "how often should I post on LinkedIn", "schedule these posts", "I have a backlog of post ideas", "spread these out", "posting strategy", "when do I publish", "build me a posting plan". Use it also when Markus has just finished a post (via the carousel skill) and the natural next question is when to ship it. Always use this skill for LinkedIn timing questions — do NOT improvise timing advice without it; the heuristics here are tuned to his specific audience.
---

# LinkedIn posting timing & strategy (Markus)

Decide *when* Markus should publish LinkedIn posts. The `linkedin-post-karusell` skill produces the post and carousel; this skill answers the next question — what time, how often, and in what order to ship a backlog.

This skill recommends slots. It does **not** write to any calendar or schedule anything automatically — Markus handles publishing himself. Calendar-conflict checking is intentionally out of scope; just give a clear recommendation and note that he should sanity-check it against his own week.

## What you can be asked for

Three modes, all handled by the same reasoning. Figure out which one applies:

1. **Single-post timing** — "when should I post this?" → recommend one specific slot (day + time + why).
2. **Cadence plan** — "how often should I post?" → recommend a sustainable rhythm.
3. **Backlog scheduling** — "schedule these N posts" → assign each a slot, properly spaced.

If it's ambiguous which mode applies, ask once, briefly. Otherwise just answer.

## Step 1 — Check for personal data, then fall back to heuristics

Before reasoning about timing, look for an engagement log at one of these paths (check in order, use the first that exists):

- a path Markus names in the conversation
- `assets/linkedin-engagement-log.json` **inside this skill folder** — the skill ships with a bundled log here, so this is the default and usually the one that applies
- `./linkedin-engagement-log.json` in the current project
- `~/linkedin-engagement-log.json`

The bundled `assets/linkedin-engagement-log.json` makes the skill self-contained: the data path works out of the box with no setup. To refresh it, replace that file (or hand over a new LinkedIn export and let the skill rebuild it). A log Markus names in conversation, or one in the project/home dir, still takes precedence if present.

Run the helper to read it and see whether there's enough signal:

```bash
python3 scripts/timing.py analyze --log <path-to-log>
```

- **If the log exists and has ≥ 10 entries**, the helper reports which weekday/hour buckets actually performed best for Markus. **Prefer this over the generic heuristics** — real data beats rules of thumb. Tell Markus you're using his own numbers.
- **If the log is missing or thin (< 10 entries)**, say so in one line and fall back to the heuristics below. Don't nag him to keep a log, but if he's never started one, mention once how to: copy `assets/engagement-log.template.json` to `~/linkedin-engagement-log.json` and append posts as he goes.

Where the numbers come from, the join you need to do on the export, the schema, and where the live log should live all live in `references/engagement-log.md` — read it before telling Markus how to log posts. The short version: the best source is LinkedIn's **Content export** (`.xlsx`); its **TOP POSTS** sheet holds two side-by-side rankings (engagement and impressions) that you **join on post URL** to get `impressions` + `engagements` per post, with real publish dates. The export has no comment split and no publish time, so the schema is two metrics and weekday-only. If Markus hands over the `.xlsx`, do the join and build the log for him.

## Step 2 — Apply the timing reasoning

The full reasoning, with the *why* behind each rule, is in `references/timing-strategy.md`. Read it before giving substantive advice — the short version below is a memory aid, not a substitute. The headline points:

- **Audience is CET-based, dev/creative-tech, Nordic + broader European.** Optimise for when *those* people open LinkedIn, not US-centric advice.
- **Best windows: Monday and Tuesday, roughly 07:30–09:00 CET** (morning commute / coffee / inbox-zero scroll) — his two strongest weekdays in the real engagement log. Secondary window ~11:30–12:30 (lunch). Wed/Thu work but have *underperformed* Mon/Tue for him, so don't treat them as prime.
- **Avoid: Friday afternoons, weekends, and after ~16:00** for this B2B-ish tech audience. Note: **Monday is NOT noisy for Markus** — the usual "avoid Monday mornings" advice is contradicted by his own numbers (Monday is his best-supported, highest-rate day). See `references/timing-strategy.md` for the data and caveats.
- **The first 60–90 minutes decide reach** — only recommend a slot Markus can realistically be awake and free to reply to early comments. His own decay curve backs this: ~half a post's reach lands on the day it goes up, two-thirds within a day, and a post is essentially spent by day 4–5 — which is also the mechanism behind the spacing rule below.
- **Cadence beats precision.** Consistent 1–2 posts/week reliably beats sporadic bursts. Protecting *spacing* matters more than shaving minutes off a clock time. His own data: ~4–7 days apart (≈weekly) is his sweet spot, tight clusters (≤2 days) underperform, and same-day double-posting costs the *second* post ~⅓ of its reach (not its engagement quality). Details + caveats in `references/timing-strategy.md`. Consistency also drives growth: months he posts average ~17 new followers vs ~5 in dark months (roughly 3×). Typical post baseline: ~1,000 impressions, ~18 engagements, ~1.8% rate.

## Step 3 — For backlog scheduling, enforce spacing

When slotting multiple posts, use the helper to lay them out so they don't bunch up:

```bash
python3 scripts/timing.py schedule --count <N> --start <YYYY-MM-DD> --per-week <1|2|3>
```

This returns candidate slots (date + time + weekday) honouring:

- a **minimum ~48h gap** between posts (back-to-back days kill the second post's reach),
- the preferred weekday/time windows,
- the requested posts-per-week ceiling.

Present the slots as a short ordered list. If Markus gave the posts in a particular order, keep it; if some are more time-sensitive (a launch, an event), say which should jump the queue.

## Step 4 — Deliver the recommendation

Keep it tight. For a single post: the slot, a one-line reason, and one caveat (e.g. "check you're not on a train then"). For a cadence plan: the rhythm + the two or three windows to rotate through. For a backlog: the ordered list of slots.

Always close by reminding Markus this is a recommendation to act on manually — the skill doesn't publish or schedule anything itself.

## References & tools

- `references/timing-strategy.md` — the full reasoning, audience model, and window rationale
- `references/engagement-log.md` — log format + how the data path works
- `scripts/timing.py` — slot maths, spacing checks, log analysis
- `assets/engagement-log.template.json` — starter log file if Markus wants the data path
