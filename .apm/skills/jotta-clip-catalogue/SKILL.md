---
name: jotta-clip-catalogue
description: >
  Turn a day's video clips into an editing-ready package and, optionally, a
  DaVinci Resolve timeline: download from Jottacloud (or use clips already on
  disk), per-clip subtitles (NB-Whisper speech + PANNs sound events), a
  structured catalogue (clips.json + catalogue.md) with visual descriptions and
  Nynorsk summaries, and an editorial cut as OTIO + location/sound SRT tracks.
  Use whenever Markus wants to pull videos off Jottacloud for a date, subtitle
  or transcribe clips, build a clip catalogue / shotlist, or edit catalogued
  footage. Triggers: "get my videos from [date]", "download the clips from
  [trip]", "subtitle these clips", "catalogue my clips", "what's in these
  videos", "prep footage for editing", "make a rough cut", "make a
  davinci/resolve timeline", "lag ein cut", "make an OTIO edit" — also when the
  clips are ALREADY downloaded. It encodes the jotta-cli listing-cap workaround,
  the macOS PANNs fix, hallucination scrubbing, and the OTIO machinery; do not
  improvise.
---

# Jotta Clip Catalogue → Resolve cut

Produces, in one day-folder:

- **Part 1 — catalogue:** raw clips (`*.mp4`), subtitles per clip (`*.srt` +
  `*.vtt`, speech and `[lyd: …]` cues), and `clips.json` + `catalogue.md`
  describing time, place, transcript, sounds, and a visual summary per clip.
- **Part 2 — editorial cut (optional):** `evidence.json`, an `edit.json`
  decision table, `<name>.otio` (imports straight into DaVinci Resolve),
  `<name>.locations.srt` + `<name>.sound.srt` (in output time), and a written
  rationale.

The hard-won parts are documented in `references/` — read before improvising:
`references/jotta-cli-notes.md` for the listing cap / album bridge / `--merge`;
`references/pipeline.md` for models, the macOS PANNs fix, hallucination
scrubbing, and the sandbox/Mac split; `references/editorial-cut.md` for the
whole edit stage.

## Defaults for Markus

- Clips come from the **Pixel** → filenames `PXL_YYYYMMDD_HHMMSS*.mp4`.
- Jottacloud: timeline at `/Photos/Timeline/<year>/<month>`, albums at
  `/Photos/Albums/<name>` (CLI case-insensitive; quote names with spaces/æøå).
- Output folder: `~/Videos/jotta-clips/<date>/` — unless the clips already live
  somewhere (e.g. `~/videos/<trip>/`); then that folder IS the out-folder.
- Norwegian speech → **NB-Whisper**; other languages → Whisper large-v3.
- Catalogue summaries in **Nynorsk**, Markus's voice (`nynorsk-skrivestil` skill).
- Cowork sandbox can't pip-install (PyPI blocked): ML stages run on the Mac,
  everything else in the sandbox. See "division of labour" in pipeline.md.

---

## Part 1 — Workflow

Run stages from the skill's `scripts/` directory; all share one `--out` folder
and every stage is idempotent/resumable.

### Preflight — never install anything yourself

```bash
python pipeline.py doctor
```

If anything is missing, show Markus the exact commands and let him run them.
In the sandbox, `pip` failing against PyPI is expected — that work moves to the
Mac (copy `pipeline.py` + needed scripts into the out-folder and hand over
`python3 ~/videos/<day>/…` commands), not to creative workarounds.

### Step 0 — Settle the inputs

Confirm: **date**; **which videos** (Pixel only, default, or all); **discovery
mode** (album / auto / both); and **are the clips already local?** Don't re-ask
what's clear from context.

### Steps 1–2 — Discover & download (skip if clips are already local)

```bash
python pipeline.py discover --date 2026-05-31 --mode both --album "Sjælland rundt" \
  --source pixel --out ~/Videos/jotta-clips/2026-05-31
python pipeline.py fetch --out ~/Videos/jotta-clips/2026-05-31
```

Modes: `album` (curated, reliable), `auto` (timeline month folder — cap-aware,
exits with a warning if the listing was truncated before the date), `both`
(album + cross-check). If truncation hits and no album exists, ask Markus to tag
the day into an album on the phone and re-run in album mode.

**Clips already on disk?** Don't re-download gigabytes:

```bash
python scripts/local_manifest.py --out ~/videos/<day> --date 2026-06-05 [--album "Name"]
```

writes manifest.json from the files and symlinks them into `clips/`.

### Step 3 — Subtitles (speech + significant sounds)

```bash
python pipeline.py subtitles --out <out>
```

Runs on the Mac. Per clip: language detect → transcribe → PANNs sound events →
`<clip>.srt/.vtt/.transcript.json`. **macOS gotcha:** PANNs fetches its models
with `wget` (absent on macOS) — speech still works, sounds silently skip. Let
the run finish, then apply the curl + `scripts/sound_pass.py` fix in
pipeline.md ("Sound events on macOS"). While the Mac churns, keep going —
Steps 4–5 don't need transcripts.

### Step 3.5 — Scrub hallucinations, then nynorskify

Whisper invents speech on engine noise. Dry-run `scripts/scrub_transcripts.py
--out <out>`, show Markus the hits, get a yes, re-run with `--apply`. Keep
genuine announcements and ambiguous exclamations.

All subtitles are delivered in **nynorsk**. After scrubbing, edit the remaining
segments in `subtitles/*.transcript.json` (your job, Claude):

- NB-Whisper writes bokmål — rewrite each Norwegian segment to standard nynorsk
  (the speaker's own words made nynorsk, not Markus's voice). Keep the original
  wording in a new `text_original` field so nothing is lost.
- Non-Norwegian speech gets a language tag plus a nynorsk translation:
  `[På engelsk] Takk for at de reiste med oss.` — language names per whisper
  code live in `scripts/labels_nn.py` (`LANG_NN`).
- Sound cues come out in nynorsk automatically (`[lyd: køyretøy]`, never
  `vehicle`) via `scripts/labels_nn.py`; copy that file alongside `pipeline.py`
  for Mac runs. If a run reports unmapped labels, translate them and extend
  `LYD_NN` in the skill rather than patching downstream.

Then regenerate every subtitle file:
`python scripts/rewrite_subs.py --out <out>`. Details in pipeline.md
("Nynorsk subtitles").

### Step 4 — Sample frames

```bash
python pipeline.py frames --out <out>
```

Representative downscaled frames per clip into `frames/<clip>/` (handles
vertical/horizontal, auto-rotated). These are what you LOOK at in Step 6.

### Step 5 — Build the catalogue skeleton

```bash
python pipeline.py catalogue-build --out <out>
```

ffprobe metadata + transcripts + sound events → `clips.json` with empty
`visual`/`summary`. **Gotcha:** this stage REBUILDS clips.json and wipes those
fields — if transcripts arrive late (Mac run, sound_pass, scrubbing), fold them
in with `scripts/merge_transcripts.py --out <out>` instead of re-running it.

### Step 6 — Fill in visual + summary (this is your job, Claude)

View each clip's frames, then write into `clips.json`:
- `visual` — concrete, factual on-screen description for an editor scanning for
  a shot. Use GPS to anchor places, and verify borderline coordinates against
  known points on the route instead of guessing.
- `summary` — one-line Nynorsk gist in Markus's voice (`nynorsk-skrivestil`).

Don't invent audio; lean on the transcript and sound events.

### Step 7 — Render & present

```bash
python pipeline.py catalogue-render --out <out>
```

Regenerates `catalogue.md`. Present `catalogue.md` + `clips.json`.

---

## Part 2 — Editorial cut (when Markus wants an edit/timeline)

Read `references/editorial-cut.md` and follow its three phases:

1. **Evidence:** Claude writes `places.json` (GPS → place names, hand-geocoded),
   then `scripts/build_evidence.py --out <out> --places places.json` →
   `evidence.json`.
2. **Reasoning:** include/drop with reasons, in/out trims, pre-speech silence
   cap, opener/closer from anywhere, setup→payoff pairs, length ceiling.
   Decisions land in `edit.json`.
3. **Render:** `scripts/build_edit.py --out <out>` → `<name>.otio` +
   `<name>.locations.srt` + `<name>.sound.srt`; write `<name>_rationale.md`;
   verify; tell Markus to import via Resolve **Timelines → Import** and add the
   srt files as subtitle tracks.

Never overwrite an earlier cut — new base name per version.

---

## Notes

- Stages are resumable; re-runs skip work already done.
- `--source all` keeps Snapchat etc.; auto mode can only date-filter Pixel
  names, so for "all videos on a date" prefer album mode.
- Everything runs locally; nothing is uploaded. The footage stays on the machine.
