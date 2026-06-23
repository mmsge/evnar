# Pipeline internals

## Install (one-time — you run this, never the skill)

The skill never installs anything. Run `python scripts/pipeline.py doctor` to see what's
missing, then install it yourself:

```bash
brew install ffmpeg
pip install -r scripts/requirements.txt --break-system-packages
```

First runs download models (cached afterwards):
- faster-whisper `large-v3` — ~1.5 GB
- NB-Whisper medium — ~1.5 GB (only fetched the first time a clip is detected Norwegian)
- PANNs SED checkpoint — ~330 MB to `~/panns_data/`

On the M5 these run on CPU (faster-whisper, int8) and MPS/Metal (NB-Whisper via
transformers). A full day of clips is comfortably an overnight-or-coffee job, not
instant — see speed tips below.

## ASR design (Step 3)

Two backends, each used for what it's best at:

- **faster-whisper `large-v3`** does language detection on every clip and transcribes
  everything that isn't Norwegian. Fast, CPU-friendly.
- **NB-Whisper** (`NbAiLab/nb-whisper-medium`, Nasjonalbiblioteket) re-transcribes clips
  detected as Norwegian (`no`/`nn`/`nb`). It's markedly better on Norwegian — including
  Nynorsk and dialect — than vanilla Whisper. If it errors, the code falls back to the
  faster-whisper transcription so you never lose a clip.

Change the model ids at the top of `pipeline.py` (`NB_WHISPER_MODEL`, `WHISPER_MODEL`).
For more speed at some accuracy cost, drop to `nb-whisper-small` and `medium`/`small`.

Toggles: `--no-asr` (skip speech entirely), `--force` (re-transcribe clips already done).

## Sound events (Step 3)

PANNs `SoundEventDetection` runs over 32 kHz audio and returns per-frame probabilities
across the 527 AudioSet classes. We threshold at `SED_THRESHOLD` (0.20), merge
contiguous active frames into events, drop anything shorter than `SED_MIN_DURATION`
(0.4 s), ignore a few unhelpful classes (`Speech`, `Music`, `Silence`, room tone —
speech is already covered by ASR), keep the 12 strongest, and emit them as
`[lyd: <label>]` cues interleaved into the SRT/VTT by timestamp.

Tune `SED_THRESHOLD` / `SED_IGNORE` near the top of `pipeline.py`. Labels are English
(AudioSet); the cue prefix is Nynorsk (`lyd`). Toggle off with `--no-sound-events`.

## Frames (Step 4)

ffmpeg samples up to `--max-frames` (default 6) evenly spaced frames per clip, fit
inside a `--max-dim` px box (default 768) preserving aspect ratio. This works for both
horizontal and vertical (9:16 / TikTok) clips, and ffmpeg auto-rotates so rotated phone
frames come out upright. Stored in `frames/<clip-stem>/fNN.jpg`. These are *the* input
for the visual descriptions in Step 6 — Claude looks at them, not the full video.

## Catalogue (Steps 5–7)

`catalogue-build` runs `ffprobe` per clip for duration, resolution, fps, capture time
(parsed from the `PXL_YYYYMMDD_HHMMSS` filename, falling back to `creation_time`), and
GPS (ISO 6709 `location` tag → lat/lon). It folds in the transcript + sound events and
writes `clips.json` sorted by capture time, with empty `visual`/`summary` fields.

Claude then views each clip's frames and fills:
- `visual` — concrete on-screen description, useful to an editor scanning for a shot
- `summary` — one-line Nynorsk gist in Markus's voice (use the `nynorsk-skrivestil` skill)

`catalogue-render` regenerates `catalogue.md` from the enriched JSON.

### clips.json schema (per clip)

```
filename, remote_path, local_path,
capture_time (ISO), duration_s, resolution, orientation, fps, gps {lat,lon}|null,
language, transcript [{start,end,text}], sound_events [{start,end,label,score}],
frames [paths], visual (str), summary (str)
```

`resolution` and `orientation` are the *displayed* values — rotation metadata is applied,
so a phone clip shot vertically reads as `1080x1920` / `vertical` even though the frames
are stored sideways.

## Output layout

```
~/Videos/jotta-clips/2026-05-31/
├── manifest.json
├── clips/            PXL_*.mp4
├── subtitles/        <clip>.srt, <clip>.vtt, <clip>.transcript.json
├── frames/<clip>/    fNN.jpg
├── clips.json
└── catalogue.md
```

## Speed tips

- Big day? Run `subtitles` and `frames` unattended; both are resumable (they skip clips
  already done), so a Ctrl-C and re-run loses nothing.
- `--no-sound-events` roughly halves Step 3 time if you only need speech.
- The whole thing is local — no upload, no API cost, footage stays on the machine.

## Sound events on macOS: the wget problem (Step 3)

`panns_inference` downloads its model files with `wget`, which macOS doesn't
ship. Symptom in the subtitles log: `sh: wget: command not found` followed by
`sound-event detection unavailable (… class_labels_indices.csv)` on every clip —
while speech transcription keeps working fine. Do NOT restart with `--force`
(that re-does the slow ASR). Instead, let the run finish, then:

```bash
mkdir -p ~/panns_data
curl -L -o ~/panns_data/class_labels_indices.csv \
  'http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv'
curl -L -o ~/panns_data/Cnn14_DecisionLevelMax.pth \
  'https://zenodo.org/record/3987831/files/Cnn14_DecisionLevelMax_mAP%3D0.385.pth?download=1'   # ~1 GB
python3 scripts/sound_pass.py --out <day-folder>
```

`sound_pass.py` redoes only the sound-event pass for clips whose transcript.json
has none, and merges into transcript.json + srt/vtt. (URLs verified against the
panns_inference source — `inference.py` and `config.py`.)

## Hallucination scrubbing (after Step 3)

Whisper-family models hallucinate on ambient noise. On a day of train footage,
NB-Whisper produced «Hva er det du gjør?» on ~15 clips, plus YouTube-outro
boilerplate («Terima kasih telah menonton», «Субтитры сделал DimaTorzok»),
film-credit lines, and free-associated nonsense — while the GENUINE audio (PA
announcements, conductor speech, the user's own exclamations) was transcribed
correctly. Review the transcripts (`scripts/scrub_transcripts.py --out DIR` is a
dry run that lists hits), show the user what would go, get a yes, then `--apply`.
Heuristics: lone generic segments on ambient-only clips are suspect; PA
announcements and salty exclamations («Fy faen.») are often real — keep
ambiguous ones. Add session-specific garbage via `--extra-pattern`.

## When the clips are already on disk

If the day's videos are already in a local folder (downloaded previously),
skip discover/fetch entirely: `scripts/local_manifest.py --out DIR --date
YYYY-MM-DD [--album NAME]` writes manifest.json from the files on disk and
symlinks them into `clips/` (the layout all later stages expect) without moving
or duplicating gigabytes.

## Sandbox / Mac division of labour (Cowork)

The Cowork sandbox usually cannot `pip install` (PyPI blocked by the network
allowlist) — so the ML stages (`subtitles`, `sound_pass.py`) must run on the
user's Mac. Everything else (frames, catalogue-build/render, local_manifest,
merge/scrub, build_evidence, build_edit) needs only ffmpeg/stdlib and runs fine
in the sandbox. The smooth pattern: copy `pipeline.py` + the needed scripts into
the day folder, give the user exact `python3 ~/videos/<day>/...` commands, and
keep working (frames, catalogue skeleton, frame viewing) while transcription
runs. The folder is shared, so results appear as they're written — poll
`subtitles/*.transcript.json` to follow progress.

## Late-arriving transcripts (gotcha)

`catalogue-build` REBUILDS clips.json and wipes `visual`/`summary`. If
transcripts/sound events arrive or change after Step 6 (Mac run finishing,
sound_pass, scrubbing), fold them in with `scripts/merge_transcripts.py --out
DIR` and re-run `catalogue-render` — never re-run catalogue-build.

## Nynorsk subtitles (Step 3.5)

The delivered subtitle tracks are nynorsk throughout — three mechanisms:

1. **Sound labels** — `scripts/labels_nn.py` maps AudioSet labels to nynorsk
   (`vehicle` → `køyretøy`, `rain on surface` → `regn mot flate`).
   `pipeline.py`, `build_edit.py` and `rewrite_subs.py` all use it (with a
   pass-through fallback if the file isn't copied along). `rewrite_subs.py`
   prints any unmapped labels; translate them and extend `LYD_NN` in the skill
   so the fix sticks for future runs.
2. **Norwegian speech** — NB-Whisper emits bokmål. Claude rewrites the kept
   segments to standard nynorsk in `transcript.json`, preserving the original
   in `text_original`. The speaker's register stays theirs (a conductor's
   announcement is formal); this is not the Markus-voice step — that's the
   catalogue `summary` field.
3. **Foreign speech** — tag + translate: `[På engelsk] <nynorsk omsetjing>`.
   Whisper-code → språknamn in `labels_nn.LANG_NN`. The per-clip `language`
   field says which code the clip was detected as.

After any transcript edit, `python3 scripts/rewrite_subs.py --out DIR`
regenerates all srt/vtt, and `scripts/merge_transcripts.py` carries the
nynorsk text into clips.json (visual/summary untouched).
