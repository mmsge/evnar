# Engagement log — the data path

The skill prefers Markus's real numbers over generic heuristics, *if* he keeps a log. This file documents where the numbers come from, the format, and how the skill uses them. Keeping a log is optional — the skill works fine on heuristics alone.

## Why bother

LinkedIn doesn't expose post analytics through any API Markus can reach from his MCP stack, so there's no automatic way to learn his real best times. A log closes that gap: with ~10 logged posts, the skill can spot which weekdays actually earn engagement and recommend from *that* instead of rules of thumb.

If he never keeps one, nothing breaks — the skill falls back to the heuristics in `timing-strategy.md`.

## Where the data comes from: the LinkedIn export (preferred)

The fastest, most accurate way to populate the log is LinkedIn's own analytics export — no manual transcription:

1. On desktop, go to **linkedin.com** and open your **analytics / creator** dashboard.
2. Find **Export** (usually a control top-right of the dashboard). Choose the **Content** report for a date range — the last 90 days is a good default.
3. You get an `.xlsx` with several sheets. The one that matters is **TOP POSTS**.

### What the export actually contains

The **TOP POSTS** sheet is *two independent rankings printed side by side*, not one aligned table:

- **Left block** (`Post URL`, `Post publish date`, `Engagements`) — the top ~14 posts ranked by engagement.
- **Right block** (`Post URL`, `Post publish date`, `Impressions`) — the top 50 posts ranked by impressions.

A post can sit at different row positions in each block, so you **join the two blocks on `Post URL`** to get impressions and engagements for the same post. Posts that appear only in the impressions block (outside the top-14 by engagement) have no engagement figure — leave `engagements` null rather than guessing.

Crucial limitations of the export:

- **No comment / reaction / reshare split.** It only gives total `Engagements` (the three lumped together). That's why the log schema uses `engagements`, not separate reaction/comment fields.
- **No publish time.** Only the publish *date*. So `posted_at` is date-only and the skill can do **weekday** analysis but not **hour-of-day** analysis from export data. (See note under Format.)
- **Impressions decay on old posts.** Posts more than a few months old show impressions decayed toward zero while engagement stays — those rows are not a real measurement. Stick to a recent window (last ~90 days) so impressions are trustworthy.

## Manual fallback (reading numbers off a post)

If you don't want to export, you can read numbers off a single post: open the post's **"View analytics"** link (in the bar under the post, by the impressions count) on desktop. The headline **Impressions** number is reliable; for `engagements`, the analytics panel gives a total. Append one record by hand. This is slower and still date-only — the export is better whenever you have more than a post or two to log.

## Format

A JSON array of post records. Copy `assets/engagement-log.template.json` to start (see "Where the log lives"). Each entry:

```json
{
  "topic": "KI-buzzwords",
  "posted_at": "2026-05-21",
  "url": "https://www.linkedin.com/feed/update/urn:li:activity:7463140292985032705",
  "impressions": 1550,
  "engagements": 22
}
```

- **`topic`** — short free-text label so you recognise the post. Not used in scoring.
- **`posted_at`** — `YYYY-MM-DD` (date-only) from the export. If you happen to know the publish time, you may instead write a full ISO-8601 timestamp with offset (e.g. `2026-05-21T08:00:00+02:00`); the analyzer will then also use it for hour-of-day. Offsets: `+02:00` in summer (CEST), `+01:00` in winter (CET).
- **`url`** — the post URL. Acts as a stable ID and lets you re-join future exports. Optional but recommended.
- **`impressions` / `engagements`** — integers. `engagements` may be null if the post wasn't in the export's engagement block; the analyzer copes.

## Where the log lives

The skill looks for the log in this order and uses the first that exists:

1. a path Markus names in the conversation,
2. `assets/linkedin-engagement-log.json` **bundled inside this skill** — ships populated, so the data path works with no setup,
3. `./linkedin-engagement-log.json` in the current project,
4. `~/linkedin-engagement-log.json` (home dir).

The skill is **self-contained**: it ships with a real log at `assets/linkedin-engagement-log.json`, so `analyze` works the moment the skill is installed. `scripts/timing.py analyze` with no `--log` auto-discovers that bundled file.

**Refreshing the data.** Replace `assets/linkedin-engagement-log.json` with an updated log — or hand the skill a fresh LinkedIn Content export and let it rebuild the file. If you'd rather keep a personal log outside the skill (so it isn't overwritten on the next skill update), put it at `~/linkedin-engagement-log.json` and name it in conversation, or in the project root; either takes precedence over the bundled copy. `assets/engagement-log.template.json` remains as a schema reference / empty starter.

## How the skill uses it

`scripts/timing.py analyze --log <path>` computes an **engagement score** per post — total engagements blended with engagement *rate* (engagements / impressions), so a post that punched above its reach is rewarded and a merely high-reach post isn't over-credited — and buckets posts by weekday (and by hour, if any entry has a real time). It reports:

- best-performing weekday(s), with the post count behind each (so confidence is visible),
- best-performing hour band(s) **only if** some entries carry a time; otherwise it says so.

With **fewer than 10 entries** the analyzer flags the sample as too thin and the skill stays on heuristics. Even at 10+, treat single-digit `n=` buckets sceptically: a weekday resting on 1-3 posts (especially event-driven ones) is a hint, not a verdict, and shouldn't overturn a heuristic on its own.

## Keeping it current

The realistic workflow: every month or so, pull a fresh **Content export** for the last 90 days, join TOP POSTS on URL, and refresh the log. The skill can do the join and rebuild the file for you if you hand it the `.xlsx`.
