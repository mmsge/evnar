# Editorial cut → DaVinci Resolve timeline

Part 2 of the skill: turn a finished catalogue into a considered edit Resolve can
open. Three phases — evidence, reasoning, rendering. The reasoning phase is
Claude's actual editing job; the scripts only feed it and serialize its decisions.

## Parameters to settle first (ask only what the user hasn't said)

- **Length ceiling** (e.g. 10 min). Treat as a ceiling, not a target — cut for
  quality. A 14-minute source day can comfortably become a 5-minute cut.
- **Output base name** (e.g. `edit_v2`). Never overwrite an earlier cut — new name.
- **Reordering allowed?** Usually yes: build a narrative arc, don't truncate
  chronology.
- **Pre-speech silence cap** (default 5 s): for clips with speech, trim the
  in-point so at most that much silence precedes the first word.

## Phase 1 — evidence layer (no edit decisions yet)

1. Write `places.json` mapping each clip stem to a place NAME (city/area, not
   coordinates) by reading the GPS in `clips.json`. Claude geocodes this itself —
   offline reverse-geocoders are rarely installed, and Claude is better. Be
   honest about uncertainty: check borderline coordinates against known station
   coordinates along the route rather than guessing from vibes. (Session lesson:
   "Nesbyen" was actually Flå.)
2. Run `scripts/build_evidence.py --out DIR --places places.json`. It folds
   clips.json + scrubbed transcripts + sound events + frame timestamps + OpenCV
   face counts into `evidence.json`, the repeatable input for everything below.
3. Report tools that were missing and how they were resolved (e.g. no `cv2` →
   face presence judged from Claude's own frame viewing; no `exiftool` → GPS
   already extracted by ffprobe in catalogue-build).

## Phase 2 — editorial reasoning (look at the frames + transcripts)

Work from `evidence.json` and the frames already viewed for the catalogue.
Re-view frames where in/out points need precision.

- **Include/drop with reasons.** Typical drops: blink-length clips (<2.5 s,
  unreadable), pocket/accident clips, vertical 9:16 clips in a 16:9 cut (format
  break — unless the cut is vertical), near-duplicate coverage (keep the
  strongest variant), murky/out-of-focus shots.
- **In/out points.** Apply the pre-speech cap; trim camera-settling at heads,
  wandering at tails, tunnel blackness, repetition. Justify each trim in one
  line — these become timeline marker notes.
- **Opener and closer.** A strong opener (establishing shot or visual hook) and
  a proper closer (sign-off, concluding line, natural wind-down) may come from
  ANYWHERE in the footage. A cold-open from the scenic peak, then chronology, is
  a reliable pattern.
- **Setup → payoff.** Scan transcripts for spoken setups (announcements,
  "wait till you see…") and make sure the payoff clip exists and comes after.
  PA/conductor announcements are gold: they narrate arrivals for free and can
  carry a finale as natural voice-over.
- **Reuse is allowed.** The same source clip may appear as two events with
  different ranges (e.g. its announcement as setup, its arrival as payoff).
- **Theme.** Look for a recurring motif in the footage (in the NDC trip it was
  the laptop/terminal — working the whole way home) and keep it alive through
  the middle.

Write the decisions as `edit.json` (schema in `scripts/build_edit.py` docstring):
ordered `events` (stem/in/out/colour/note), `dropped` (stem/why), and
`setup_payoff` pairs. Colour markers meaningfully: PURPLE opener/closer, ORANGE
setup/payoff, GREEN ordinary.

## Phase 3 — render and hand over

1. `python3 scripts/build_edit.py --out DIR` → `<name>.otio` (V1 + mirrored A1,
   markers with notes), `<name>.locations.srt`, `<name>.sound.srt`, and a
   printed summary (order, in/out, runtime, pairs, drops).
2. Write `<name>_rationale.md`: structure/acts, setup→payoff table, what the
   pre-speech rule did, drops, adaptations from the original brief, technical
   notes. The user reviews this before opening Resolve.
3. Verify before handing over: every source_range within its available_range,
   A1 mirrors V1, totals under the ceiling, srt cue count sane.
4. Tell the user: import the `.otio` via **Timelines → Import** in Resolve, add
   the two srt files as subtitle tracks, and leave the source clips where they
   are (the OTIO references them by `file://` absolute path — non-destructive,
   nothing re-encoded).

## Technical notes (get these right)

- **No opentimelineio dependency.** `build_edit.py` writes the OTIO JSON schema
  directly (Timeline.1 / Stack.1 / Track.1 / Clip.1 / ExternalReference.1 /
  Marker.2). Resolve imports it fine; verified against otio-written files.
- **Rates:** each clip's `source_range` uses its own native fps from ffprobe
  (Pixel footage mixes 29.67–240 fps); the timeline rate (default 30) only
  governs marker positions. 120/240 fps clips import at normal speed — mention
  to the user they can retime for slow-mo.
- **SRT files are in OUTPUT time** — cumulative position in the assembled cut,
  not source time. `build_edit.py` accumulates this; never hand-compute.
- **media_dir must be the HOST-side absolute path** (`/Users/markus/...`), not a
  sandbox mount path — Resolve runs on the Mac.
