# Timing strategy — the reasoning

This is the substance behind the slot recommendations. Read it before giving advice so the recommendations come with a *why*, not just a clock time.

## The audience model

Markus's LinkedIn following is shaped by where he actually operates:

- **Geography:** Norway-centred (Bergen), spilling into the broader Nordics and Europe. Treat **CET/CEST** as the reference timezone for every recommendation.
- **Profession:** software dev + creative-tech. Self-hosting, open source, Norwegian-language tooling, the NDC/conference circuit, Mastodon/fediverse (skvip.lol), Codeberg, the Krins webring crowd.
- **Behaviour:** this is a B2B-ish professional audience that opens LinkedIn during the working day, not a consumer/evening-scroll audience. That single fact drives most of the timing.

Because the audience is European, **ignore US-centric "best time to post" advice** even though it dominates the search results. A slot optimised for US Eastern time lands in the European evening, which is dead for this crowd.

### His baseline numbers (yardstick for judging a post)

From the engagement log, a *typical* Markus post lands around **1,000 impressions, ~18 engagements, ~1.8% engagement rate**. The middle half of his posts span roughly **520–1,650 impressions** and **1.1–2.5% rate**; his ceiling so far is ~2,600 impressions / 61 engagements (~680 followers as of the latest export). Use this to put a result in context rather than judging in a vacuum: above ~2.5% rate or ~1,650 impressions is a genuine hit for him; below ~1.1% rate is a dud worth not repeating. Refresh these figures whenever the log is rebuilt from a new export.

## Why timing matters at all

LinkedIn's feed rewards early velocity: the engagement a post earns in roughly its **first 60–90 minutes** strongly predicts how far the algorithm pushes it afterward. Two consequences:

1. Post when your audience is *already on the app*, so the early window catches real eyes.
2. Only pick a slot when Markus can be **free to reply** to the first few comments — responding early compounds reach. A perfectly-timed post he can't tend to underperforms one posted when he's at his desk.

### What Markus's own numbers say about reach decay (from the daily impressions series)

His posts confirm how front-loaded this is. Tracing the daily impressions of isolated posts (ones with a quiet stretch after, so the curve isn't muddied by a follow-up), normalised to the post day:

| | day 0 | +1 | +2 | +3 | +4 | +5 | +6 |
|---|---|---|---|---|---|---|---|
| share of day-0 reach | 100% | ~37% | ~20% | ~15% | ~19% | ~8% | ~7% |
| cumulative share of the week | 49% | 66% | 76% | 83% | 93% | 97% | 100% |

Read-out: **~half his reach lands on the day he posts, two-thirds within a day, three-quarters within two days, and a post is essentially spent by day 4–5.** This is the mechanism behind the rest of the skill — it's *why* the first-day slot matters so much, *why* the ~48h floor exists (a day-old post is still pulling 20–37% of its opening reach, so a back-to-back post competes with it), and *why* ~weekly spacing is the sweet spot (by 5–7 days the previous post has cleared the feed). Caveat: n=4 isolated posts, the day-4 figure is inflated by one post's anomalous second-wind bump, and one post is truncated by the export's end date — treat the curve as approximate, but the front-loaded shape holds across all four.

## The windows

Ranked best-to-worst for this audience:

| Window | Day(s) | Why |
|---|---|---|
| **07:30–09:00 CET** ⭐ | Mon, Tue | Commute + coffee + inbox-zero scroll. His two strongest weekdays in the real data (see below). The prime slot. |
| 11:30–12:30 CET | Mon, Tue | Lunch dip. Solid secondary option. |
| 07:30–09:00 CET | Wed, Thu | Fine, but for *Markus specifically* these have underperformed Mon/Tue — don't treat them as prime the way generic advice does. |
| Anytime | Fri | High variance: the odd Friday post lands well, most tail off. AM only, and don't rely on it. |
| Anytime | Sat, Sun | Largely dead for a professional/tech audience. Avoid. |
| After ~16:00 CET | Any | The audience is logging off. Avoid for primary posts. |

**Default recommendation when in doubt: Monday or Tuesday, ~08:00 CET.**

### What Markus's own numbers say (from the LinkedIn export, ~18 in-window posts)

This table's weekday ranking is **backed by his real data**, not generic wisdom — and the data overturned the usual rule. Running `timing.py analyze` on his engagement log, the two clear top weekdays by blended engagement score are **Tuesday (avg ~32, n=3)** and **Monday (avg ~30, n=5)**. Monday is also his **highest engagement-*rate* day (~2.8%)** and his best-supported bucket. Wednesday and Thursday actually sit near the *bottom* for him — the opposite of the "Tue–Thu is prime, Monday is noisy" advice you'll read everywhere. So for Markus, **Monday is not noisy; it's a top slot.**

Caveats, so this isn't over-read:

- **Weekday only, no hour-of-day** — the export carries publish *date* but no time, so none of this validates a specific clock hour. The 07:30–09:00 window is still audience-model reasoning, not data-derived.
- **Small, content-confounded samples** (n=3–5 per day). Tuesday's peak leans heavily on one viral reflective post; Monday's strength includes event-driven SognaCon/NDC posts. Treat the Mon/Tue lead as solid but the finer ordering as soft.
- Re-run `analyze` after each export refresh — if a future window shifts the ranking, update this table to follow the numbers.

If Markus names a different engagement log in conversation, that one overrides this table — people's real audiences are quirkier than any rule.

## Cadence — the part that actually matters most

For an account Markus's size, *consistency* moves the needle far more than optimising the clock. The failure modes to design against:

- **Bursting:** the batch idea-generator produces several posts, he ships three in two days, then goes quiet. The later posts cannibalise the earlier ones' reach, and the quiet stretch loses momentum.
- **Going dark:** weeks with nothing, so the audience forgets him and the algorithm deprioritises the account. His own numbers put a cost on this: **months he posted at least once averaged ~17 new followers; dark months averaged ~5** — posting roughly *triples* his follower-acquisition rate. (Confounded — he posts more when something's happening, and events draw followers on their own — but the gap is large and one-directional, so silence plausibly stalls growth, not just reach.)

Recommended cadence:

- **Sweet spot: 1–2 posts per week.** Sustainable alongside everything else he's building, and frequent enough to stay visible.
- **Hard ceiling: 3 per week.** Beyond that, posts compete with each other and quality usually drops.
- **Minimum spacing: ~48 hours between posts; aim for ~weekly.** Back-to-back days reliably hurt the *second* post — and his own numbers show the cost is in **reach, not engagement quality** (see the spacing data below). His best-performing gap is ~4–7 days. The `timing.py schedule` command enforces the 48h floor.

When advising on cadence, frame it as *rhythm over perfection*: a standing "Monday + Wednesday morning" habit he can keep beats a theoretically-optimal schedule he can't. (Monday is his strongest day; the second-best day, Tuesday, sits right next to it, so a twice-weekly rhythm can't use both without breaking the ~48h spacing below — Wednesday is the nearest slot that keeps the gap. This is exactly what `timing.py schedule --per-week 2` produces.)

### What Markus's own numbers say about spacing (from the log, n≈17 with a measurable gap)

A gap analysis on the engagement log (bucketing each post by **days since the previous post**) backs the spacing rule and sharpens it:

- **~4–7 days apart is his sweet spot** — the best bucket on both engagement (avg ~31) and rate (~2.4%), comfortably ahead of tighter spacing. Essentially a weekly rhythm.
- **Tight clusters (≤2 days) underperform spaced posts (≥3 days):** ~15 vs ~23 avg engagements, ~1.7% vs ~2.1% rate. Almost all his sub-1.5%-rate posts fall in the May–June stretch where he posted every 1–2 days.
- **Same-day double-posting is the clearest cost.** On 2 Mar 2026 he posted twice: the first got 35 engagements / 900 impressions, the second 23 / 592 — an *identical 3.9% engagement rate*, but the second reached a third fewer people. The penalty is **distribution, not content quality** — the feed throttled the second post's reach, not its appeal. So the takeaway isn't "the second post was worse," it's "don't make the feed choose."

Caveats, so this isn't over-read: small sample, and the gap is confounded with content type and with that one dense May–June burst — can't cleanly separate "posted too soon" from "weaker post." Treat it as a firm nudge toward weekly spacing and a clear steer against same-day / back-to-back posting, not a precise dose-response curve. Re-run the gap check after each export refresh to see if it holds.

## Matching slot to content

Minor tuning once the window is chosen:

- **Launches / "the thing is now live" posts** — lead the week (Tue), so there's runway for follow-up engagement before the weekend.
- **Reflective / build-story / observation posts** — these don't need launch runway, so they're the natural fill for the non-launch slot. Don't reflexively bury them mid-week (Wed/Thu) just because generic advice calls those slots "safe" — his single best post ever was exactly this kind, posted on a Tuesday. A strong day suits them as much as a launch.
- **Time-sensitive posts** (tied to an event, a conference like NDC, a date) — those jump the queue regardless of the ideal weekday. Relevance beats the heuristic.

## What this skill deliberately does NOT do

- It does **not** check his calendar or detect travel conflicts — that was a deliberate scoping choice. Always remind him to eyeball the slot against his own week (he travels by rail a lot, and a post he can't tend to from a train underperforms).
- It does **not** publish or schedule anything. Every output is a recommendation he acts on manually.
