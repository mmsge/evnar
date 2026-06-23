#!/usr/bin/env python3
"""Timing helper for the linkedin-post-timing skill.

Two sub-commands:

  analyze  [--log PATH]
      Read an engagement log and report which weekday/hour buckets perform
      best for Markus. If --log is omitted, auto-discovers the bundled log
      (assets/), then a project-local file, then ~/. Falls back gracefully
      if the log is missing or thin.

  schedule --count N --start YYYY-MM-DD [--per-week 1|2|3]
      Lay out N posting slots from the start date, honouring the preferred
      weekday/time windows, the per-week ceiling, and a ~48h minimum gap.

No external dependencies — standard library only.
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, time
from pathlib import Path


def default_log_path():
    """Resolve the log to use when --log isn't given.

    Order: bundled log inside the skill (assets/linkedin-engagement-log.json),
    then a project-local file, then ~/linkedin-engagement-log.json. Returns the
    first that exists, or None. A path named on the command line overrides all
    of this.
    """
    here = Path(__file__).resolve().parent           # scripts/
    candidates = [
        here.parent / "assets" / "linkedin-engagement-log.json",  # bundled
        Path.cwd() / "linkedin-engagement-log.json",              # project
        Path.home() / "linkedin-engagement-log.json",             # home
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


# --- Heuristic windows (CET/CEST). Mon=0 .. Sun=6 -------------------------

# Preferred posting days in priority order: Mon, Tue, then Wed, Thu.
# (Markus's real engagement log: Mon & Tue are his two strongest weekdays;
#  Wed/Thu trail. Fri is high-variance and weekends are dead, so both are
#  left out of the rotation. Re-derive from `analyze` if a refresh shifts this.)
PREFERRED_DAYS = [0, 1, 2, 3]
# Primary time window start (local). 08:00 is the default pick.
PRIMARY_TIME = time(8, 0)
MIN_GAP_HOURS = 48
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]


# --- schedule -------------------------------------------------------------

def schedule(count, start, per_week):
    """Yield `count` slots starting on/after `start`.

    Works week by week. Within each ISO week it picks the highest-priority
    preferred weekdays first (Mon > Tue > Wed > Thu), so a backlog leads with
    strong days rather than whatever preferred day happens to come first
    chronologically. Caps at `per_week` posts per week and never places two
    posts within MIN_GAP_HOURS of each other.
    """
    slots = []
    # Start of the ISO week (Monday) containing `start`.
    week_start = (start - timedelta(days=start.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0)
    guard = 0
    while len(slots) < count and guard < 60:  # up to ~60 weeks
        guard += 1
        placed_this_week = 0
        # Try preferred days in PRIORITY order, not chronological order.
        for wd in PREFERRED_DAYS:
            if len(slots) >= count or placed_this_week >= (per_week or 99):
                break
            day = week_start + timedelta(days=wd)
            candidate = datetime.combine(day.date(), PRIMARY_TIME)
            if candidate < start:
                continue
            if slots and (candidate - slots[-1]) < timedelta(hours=MIN_GAP_HOURS):
                continue
            slots.append(candidate)
            placed_this_week += 1
        # Keep slots in chronological order for output.
        slots.sort()
        week_start += timedelta(days=7)
    return slots[:count]


def print_schedule(slots, requested):
    if not slots:
        print("No slots produced — check the start date.")
        return
    print(f"Suggested slots ({len(slots)} of {requested} requested):\n")
    for i, s in enumerate(slots, 1):
        print(f"  {i}. {WEEKDAY_NAMES[s.weekday()]} {s:%Y-%m-%d} at {s:%H:%M} CET")
    if len(slots) < requested:
        print(f"\n(Only {len(slots)} fit cleanly in range; extend the horizon "
              f"or raise --per-week for more.)")
    print("\nReminder: these are recommendations. Eyeball each against your "
          "own week before publishing — the skill doesn't check your calendar.")


# --- analyze --------------------------------------------------------------

def _score(entry):
    """Engagement score for a post.

    The LinkedIn data export gives total `engagements` per post (reactions +
    comments + reshares lumped together) but not the split, so we score on
    that directly. Engagement *rate* (engagements per impression) is the
    fairer signal — it isn't inflated by a post that simply got lots of reach
    — so we blend the raw count with the rate.

    Older logs that predate the export and carry the reactions/comments/
    reshares split still work: if `engagements` is absent we reconstruct it
    from those fields.
    """
    imp = entry.get("impressions", 0) or 0
    eng = entry.get("engagements")
    if eng is None:
        # Back-compat with the old hand-transcribed schema.
        eng = ((entry.get("reactions", 0) or 0)
               + (entry.get("comments", 0) or 0)
               + (entry.get("reshares", 0) or 0))
    rate = (eng / imp) if imp else 0
    # Raw engagements carry the signal; the rate term (scaled up) rewards
    # posts that punched above their reach.
    return eng + rate * 100


def analyze(log_path):
    try:
        with open(log_path) as f:
            entries = json.load(f)
    except FileNotFoundError:
        print(f"NO_LOG: no file at {log_path}. Use heuristics.")
        return
    except (json.JSONDecodeError, OSError) as e:
        print(f"BAD_LOG: could not read {log_path} ({e}). Use heuristics.")
        return

    if not isinstance(entries, list):
        print("BAD_LOG: expected a JSON array. Use heuristics.")
        return

    n = len(entries)
    if n < 10:
        print(f"THIN_LOG: only {n} entries (need >=10 for signal). "
              f"Use heuristics; mention the log exists.")
        return

    by_day = defaultdict(list)
    by_hour = defaultdict(list)
    hour_known = 0
    for e in entries:
        raw = e.get("posted_at", "")
        try:
            dt = datetime.fromisoformat(raw)
        except (KeyError, ValueError):
            continue
        s = _score(e)
        by_day[dt.weekday()].append(s)
        # A date-only value (no "T", or midnight from a bare date) carries no
        # real hour-of-day. The LinkedIn export is date-only, so most entries
        # land here — only count an hour when the source actually had a time.
        if "T" in raw or (":" in raw):
            by_hour[dt.hour].append(s)
            hour_known += 1

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0

    day_rank = sorted(by_day.items(), key=lambda kv: avg(kv[1]), reverse=True)
    hour_rank = sorted(by_hour.items(), key=lambda kv: avg(kv[1]), reverse=True)

    print(f"DATA_OK: {n} posts analysed.\n")
    print("Best weekdays (by avg engagement score):")
    for day, scores in day_rank[:3]:
        print(f"  {WEEKDAY_NAMES[day]:9} avg {avg(scores):7.1f}  (n={len(scores)})")
    if hour_known:
        print("\nBest hours of day:")
        for hour, scores in hour_rank[:3]:
            print(f"  {hour:02d}:00     avg {avg(scores):7.1f}  (n={len(scores)})")
    else:
        print("\nNo hour-of-day signal: entries are date-only (the LinkedIn "
              "export omits publish time). Weekday analysis above is valid; "
              "for hour analysis, note publish times on future posts.")
    print("\nUse these over the generic heuristics — they're Markus's real numbers.")


# --- cli ------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="LinkedIn posting timing helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze")
    a.add_argument("--log", default=None,
                   help="Path to the engagement log. If omitted, auto-discovers "
                        "the bundled log, then project, then home dir.")

    s = sub.add_parser("schedule")
    s.add_argument("--count", type=int, required=True)
    s.add_argument("--start", required=True, help="YYYY-MM-DD")
    s.add_argument("--per-week", type=int, default=2, choices=[1, 2, 3])

    args = p.parse_args()

    if args.cmd == "analyze":
        log = args.log or default_log_path()
        if not log:
            print("NO_LOG: no log named and none found in the usual places. "
                  "Use heuristics.")
            return
        analyze(log)
    elif args.cmd == "schedule":
        try:
            start = datetime.strptime(args.start, "%Y-%m-%d")
        except ValueError:
            print("Bad --start; expected YYYY-MM-DD.")
            sys.exit(1)
        slots = schedule(args.count, start, args.per_week)
        print_schedule(slots, args.count)


if __name__ == "__main__":
    main()
