---
name: lastfm-scrobble-report
description: >
  Generate a comprehensive Last.fm scrobble report for any artist in the user's
  listening history. Produces a colour-coded PDF with per-album track tables and
  charts, plus a companion CSV. Use this skill whenever the user asks to analyse
  their Last.fm scrobbles for a specific artist, wants to know how many times
  they've played an artist's albums or tracks, asks for a "scrobble report",
  "listening report", or "Last.fm breakdown" for an artist — even if they don't
  explicitly say "PDF" or "CSV". Always use this skill for these requests; do not
  attempt to build the workflow from scratch.
compatibility: "Requires Last.fm MCP (get_album_info, get_track_info). Python packages: reportlab, matplotlib, pillow (auto-installed if missing)."
---

# Last.fm Scrobble Report

Generates a per-artist scrobble report: one PDF (charts + tables) and one CSV,
covering every studio album including deluxe editions and pre-release singles.

## Quick overview of the workflow

1. **Gather album/track data** from Last.fm MCP
2. **Handle edge cases** (separate singles, deluxe bonus tracks, API encoding issues)
3. **Generate outputs** using the script in `scripts/generate_report.py`

Read `references/workflow.md` for the full step-by-step data-gathering process.
Read `references/known_issues.md` for common Last.fm API gotchas.

---

## Step 1 — Collect artist and album information

Ask the user (or infer from context):
- **Artist name** — exact spelling as it appears on Last.fm
- **Last.fm username** — default to `mvrkws` for Markus
- **Albums to include** — by default include all studio albums; ask if they want
  EPs, compilations, or soundtracks included too

Then use `get_artist_info` to confirm the artist exists and note the canonical
name spelling Last.fm uses.

---

## Step 2 — Build the tracklist

For each studio album:

1. Call `get_album_info(artist, album, username)` to get the Last.fm album entry
   and its track list + your play count.
2. Note which tracks Last.fm's album entry **omits** (common for tracks 11+ on
   longer albums, or tracks that charted as singles before the album). These must
   be fetched individually.
3. If a **Deluxe edition** exists, call `get_album_info` on it too. Compare track
   lists — only fetch the *new* bonus tracks individually (avoid double-counting
   the base tracks).
4. For each **pre-release single** not on the standard album, call `get_track_info`
   individually and add it as a separate row annotated "Pre-release single".
5. For any **standalone single** released between albums (e.g. "Two Weeks Ago" for
   The Good Witch), fetch individually and annotate "Single (not on album)".

See `references/workflow.md` for tips on finding what singles exist.

---

## Step 3 — Fetch individual track scrobbles

Call `get_track_info(artist, track, username)` for every track not already
covered by the album entry. This includes:
- Tracks missing from the Last.fm album entry
- Deluxe bonus tracks
- Pre-release singles
- Standalone singles

**Apostrophe encoding issue**: Some track names with curly apostrophes (e.g.
`I'm Trying (Not Friends)`) return 0 plays even when plays exist. See
`references/known_issues.md` for the full explanation and mitigation strategy.

---

## Step 4 — Generate the report

Install dependencies if needed:
```bash
pip install reportlab matplotlib pillow --break-system-packages -q
```

Then call the generation script — see `scripts/generate_report.py`.

Pass all collected data as a Python dict matching the schema in
`references/data_schema.md`.

The script outputs:
- `<artist_slug>_scrobbles.pdf` — multi-page PDF report
- `<artist_slug>_scrobbles.csv` — flat CSV of all track data

Copy both to `/mnt/user-data/outputs/` and present them with `present_files`.

---

## Colour palette (per album)

The script assigns colours automatically cycling through this palette:

| Slot | Hex | Label |
|------|-----|-------|
| 1 | `#6c5ce7` | Purple |
| 2 | `#00b894` | Green |
| 3 | `#e17055` | Coral |
| 4 | `#0984e3` | Blue |
| 5 | `#fd79a8` | Pink |
| 6 | `#fdcb6e` | Gold |

Deluxe bonus tracks always use `#fdcb6e` (gold).
Unresolvable tracks use `#b2bec3` (grey).
Standalone singles use `#74b9ff` (light blue).
