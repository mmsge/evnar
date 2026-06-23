#!/usr/bin/env python3
"""
jotta-clip-catalogue pipeline.

Stages (each a subcommand, all idempotent, all share one --out working folder):

    discover          enumerate a date's clips -> manifest.json
    fetch             download clips by exact path (jotta-cli --merge)
    subtitles         ASR (NB-Whisper / Whisper) + sound events -> .srt/.vtt/.transcript.json
    frames            sample representative frames per clip
    catalogue-build   ffprobe + transcripts -> clips.json (+ skeleton catalogue.md)
    catalogue-render  enriched clips.json -> final catalogue.md

Run from the skill's scripts/ directory. See ../references/pipeline.md for details.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------------- #
# Config / constants
# ----------------------------------------------------------------------------- #

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".3gp", ".mkv", ".webm", ".avi"}
try:
    from labels_nn import lyd_label
except ImportError:                      # pipeline.py copied out alone
    def lyd_label(label: str) -> str:
        return label.lower()

TIMELINE_BASE = "/Photos/Timeline"
ALBUM_BASE = "/Photos/Albums"

# jotta-cli `ls` silently caps long listings. When a month listing returns at least
# this many entries we treat it as "probably capped" and stop trusting completeness.
CAP_SOFT_LIMIT = 800

# ASR model ids
NB_WHISPER_MODEL = "NbAiLab/nb-whisper-medium"   # Norwegian (Nasjonalbiblioteket)
WHISPER_MODEL = "large-v3"                        # faster-whisper, everything else
NORWEGIAN_LANGS = {"no", "nn", "nb", "nor"}

# Sound-event detection
SED_THRESHOLD = 0.20          # min probability for a class to count as "present"
SED_MIN_DURATION = 0.4        # seconds; ignore blips shorter than this
SED_IGNORE = {"Speech", "Inside, small room", "Silence", "Music"}  # Speech handled by ASR

PXL_RE = re.compile(r"PXL_(\d{8})_(\d{6})(\d{3})?", re.IGNORECASE)

# Dependencies. This skill NEVER installs anything itself — it only reports what's
# missing and prints the commands for the user to run.
REQUIRED_BINARIES = ["jotta-cli", "ffmpeg", "ffprobe"]
REQUIRED_PYPKGS = {            # import name -> pip name
    "faster_whisper": "faster-whisper",
    "transformers": "transformers",
    "torch": "torch",
    "librosa": "librosa",
    "panns_inference": "panns-inference",
    "numpy": "numpy",
}
ASR_PYPKGS = {"faster_whisper": "faster-whisper", "transformers": "transformers",
              "torch": "torch"}


# ----------------------------------------------------------------------------- #
# Small helpers
# ----------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(msg, flush=True)


def die(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[name-defined]
    print(f"error: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def run(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command. cmd is a list (no shell), so spaces / æøå in args are safe."""
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
    )


def have(binary: str) -> bool:
    from shutil import which
    return which(binary) is not None


def missing_pypkgs(pkgs: dict) -> list[str]:
    """Return the pip names of packages that aren't importable. Does NOT install them."""
    return [pip_name for mod, pip_name in pkgs.items()
            if importlib.util.find_spec(mod) is None]


def out_dir(args) -> Path:
    d = Path(os.path.expanduser(args.out))
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, obj) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def is_video(name: str) -> bool:
    return Path(name).suffix.lower() in VIDEO_EXTS


# ----------------------------------------------------------------------------- #
# jotta-cli wrappers
# ----------------------------------------------------------------------------- #

def jotta_ls(remote_path: str) -> list[dict]:
    """Return the Files entries of a jotta-cli listing. Empty list on error."""
    if not have("jotta-cli"):
        die("jotta-cli not found on PATH. Install it and `jotta-cli login` first.")
    cp = run(["jotta-cli", "ls", remote_path, "--json"])
    if cp.returncode != 0:
        die(f"jotta-cli ls failed for {remote_path!r}:\n{cp.stderr.strip()}")
    try:
        data = json.loads(cp.stdout)
    except json.JSONDecodeError:
        die(f"could not parse jotta-cli JSON for {remote_path!r}")
    files = data.get("Files") or []
    return files


def jotta_download(remote_path: str, dest: Path) -> subprocess.CompletedProcess:
    """Fire an async download. jotta-cli queues these; we wait separately by size."""
    return run(["jotta-cli", "download", remote_path, str(dest), "--merge"], capture=True)


# ----------------------------------------------------------------------------- #
# Stage: discover
# ----------------------------------------------------------------------------- #

def _date_compact(date_str: str) -> str:
    """'2026-05-31' -> '20260531'."""
    return date_str.replace("-", "")


def _month_path(date_str: str) -> str:
    y, m, _ = date_str.split("-")
    return f"{TIMELINE_BASE}/{int(y)}/{int(m)}"   # CLI uses unpadded month, e.g. /2026/5


def _files_to_manifest(files: list[dict], source: str, date_str: str | None) -> list[dict]:
    out = []
    compact = _date_compact(date_str) if date_str else None
    for f in files:
        name = f.get("Name", "")
        if not is_video(name):
            continue
        if source == "pixel" and not name.upper().startswith("PXL_"):
            continue
        # In album mode date is None (album is already curated). In auto mode we
        # only keep clips whose filename carries the requested date.
        if compact is not None:
            mo = PXL_RE.search(name)
            if not mo or mo.group(1) != compact:
                continue
        out.append({
            "name": name,
            "remote_path": f.get("Path", ""),
            "size": f.get("Size", 0),
            "modified": f.get("Modified", 0),
        })
    # de-dupe by name, stable
    seen, uniq = set(), []
    for c in sorted(out, key=lambda c: c["name"]):
        if c["name"] in seen:
            continue
        seen.add(c["name"])
        uniq.append(c)
    return uniq


def _auto_discover(date_str: str, source: str) -> tuple[list[dict], dict]:
    """Auto mode: list the month folder, filter by date. Returns (clips, cap_report)."""
    month = _month_path(date_str)
    files = jotta_ls(month)
    names = [f.get("Name", "") for f in files]

    # Determine the newest PXL capture-date that made it under the listing cap.
    dates_present = sorted({m.group(1) for n in names if (m := PXL_RE.search(n))})
    max_date = dates_present[-1] if dates_present else None
    want = _date_compact(date_str)

    capped = len(files) >= CAP_SOFT_LIMIT
    report = {
        "month_path": month,
        "entries_returned": len(files),
        "looks_capped": capped,
        "newest_date_in_listing": max_date,
        "requested_date": want,
    }
    if max_date is not None:
        if want > max_date:
            report["truncated"] = True   # date is entirely beyond the cap
        elif want == max_date and capped:
            report["possibly_incomplete"] = True  # date sits right at the cap edge
    clips = _files_to_manifest(files, source, date_str)
    return clips, report


def _album_discover(album: str, source: str) -> list[dict]:
    files = jotta_ls(f"{ALBUM_BASE}/{album}")
    # Album is already curated to the day, so no date filter.
    return _files_to_manifest(files, source, None)


def cmd_discover(args) -> None:
    d = out_dir(args)
    mode = args.mode
    clips: list[dict] = []

    if mode in ("album", "both") and args.album:
        log(f"album mode: /Photos/Albums/{args.album}")
        album_clips = _album_discover(args.album, args.source)
        log(f"  album has {len(album_clips)} matching video(s)")
        clips = album_clips

    if mode == "auto" or (mode == "both" and not args.album):
        log(f"auto mode: deriving month folder from {args.date}")
        auto_clips, report = _auto_discover(args.date, args.source)
        log(f"  listing returned {report['entries_returned']} entries; "
            f"newest date seen = {report.get('newest_date_in_listing')}")
        if report.get("truncated"):
            die(
                f"the {args.date} clips are beyond jotta-cli's listing cap "
                f"(listing stops at {report.get('newest_date_in_listing')}).\n"
                f"Switch to album mode: tag the day's videos into a Jottacloud album on "
                f"the phone, wait for it to sync, then re-run with "
                f"--mode album --album \"<name>\"."
            )
        if report.get("possibly_incomplete"):
            log("  WARNING: the requested date sits at the cap edge — the listing may "
                "be missing some of its clips. Album mode is safer for completeness.")
        clips = auto_clips

    elif mode == "both" and args.album:
        # cross-check the album against what auto can see (best-effort, non-fatal)
        try:
            auto_clips, _ = _auto_discover(args.date, args.source)
            album_names = {c["name"] for c in clips}
            extra = [c["name"] for c in auto_clips if c["name"] not in album_names]
            if extra:
                log(f"  note: auto found {len(extra)} clip(s) not in the album: "
                    f"{', '.join(extra[:5])}{'…' if len(extra) > 5 else ''}")
        except SystemExit:
            log("  (auto cross-check skipped — month listing unavailable)")

    if not clips:
        die("no clips discovered. Check the date, --source, and album name.")

    manifest = {
        "date": args.date,
        "mode": mode,
        "album": args.album,
        "source": args.source,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "clips": clips,
    }
    save_json(d / "manifest.json", manifest)
    total_mb = sum(c["size"] for c in clips) / 1e6
    log(f"\n{len(clips)} clip(s), ~{total_mb:.0f} MB → {d/'manifest.json'}")
    for c in clips:
        log(f"  {c['name']}  ({c['size']/1e6:.0f} MB)")


# ----------------------------------------------------------------------------- #
# Stage: fetch
# ----------------------------------------------------------------------------- #

def cmd_fetch(args) -> None:
    d = out_dir(args)
    manifest = load_json(d / "manifest.json")
    clips = manifest["clips"]
    clips_dir = d / "clips"
    clips_dir.mkdir(exist_ok=True)

    pending = []
    for c in clips:
        target = clips_dir / c["name"]
        if target.exists() and target.stat().st_size == c["size"]:
            continue  # already complete
        pending.append(c)

    if not pending:
        log(f"all {len(clips)} clip(s) already present in {clips_dir}")
        return

    log(f"queuing {len(pending)} download(s) (jotta-cli runs them one at a time)…")
    for c in pending:
        cp = jotta_download(c["remote_path"], clips_dir)
        if cp.returncode != 0:
            log(f"  WARN could not queue {c['name']}: {cp.stderr.strip()}")

    # Wait for completion by comparing on-disk size to the manifest size.
    deadline = time.time() + args.timeout
    log("waiting for downloads to finish (Ctrl-C is safe; re-run to resume)…")
    while time.time() < deadline:
        done = [c for c in clips
                if (clips_dir / c["name"]).exists()
                and (clips_dir / c["name"]).stat().st_size == c["size"]]
        log(f"  {len(done)}/{len(clips)} complete")
        if len(done) == len(clips):
            log("all downloads complete.")
            return
        time.sleep(args.poll)

    missing = [c["name"] for c in clips
               if not ((clips_dir / c["name"]).exists()
                       and (clips_dir / c["name"]).stat().st_size == c["size"])]
    log(f"\nTimed out. Still incomplete ({len(missing)}): {', '.join(missing)}")
    log("Check `jotta-cli list downloads` for queued/failed jobs, then re-run fetch.")


# ----------------------------------------------------------------------------- #
# Stage: subtitles (ASR + sound events)
# ----------------------------------------------------------------------------- #

def _extract_wav(clip: Path, wav: Path) -> None:
    run(["ffmpeg", "-y", "-i", str(clip), "-ac", "1", "-ar", "16000",
         "-vn", str(wav)], capture=True)


_fw_model = None      # cached faster-whisper model
_nb_pipe = None       # cached NB-Whisper transformers pipeline


def _faster_whisper():
    global _fw_model
    if _fw_model is None:
        from faster_whisper import WhisperModel
        log("  loading faster-whisper (large-v3)…")
        _fw_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _fw_model


def _nb_whisper():
    global _nb_pipe
    if _nb_pipe is None:
        import torch
        from transformers import pipeline
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        log(f"  loading NB-Whisper ({NB_WHISPER_MODEL}) on {device}…")
        _nb_pipe = pipeline(
            "automatic-speech-recognition",
            model=NB_WHISPER_MODEL,
            device=device,
            chunk_length_s=28,
            return_timestamps=True,
        )
    return _nb_pipe


def _transcribe(wav: Path) -> tuple[str, list[dict]]:
    """Return (language, segments[{start,end,text}])."""
    model = _faster_whisper()
    segments_iter, info = model.transcribe(str(wav), vad_filter=True)
    lang = (info.language or "").lower()

    if lang in NORWEGIAN_LANGS:
        # Re-transcribe with NB-Whisper for better Norwegian.
        try:
            res = _nb_whisper()(str(wav), generate_kwargs={"language": "no"})
            segs = []
            for ch in res.get("chunks", []):
                ts = ch.get("timestamp", (None, None))
                segs.append({
                    "start": ts[0] or 0.0,
                    "end": ts[1] or (ts[0] or 0.0),
                    "text": ch.get("text", "").strip(),
                })
            if segs:
                return lang, segs
        except Exception as e:  # fall back to faster-whisper result
            log(f"  NB-Whisper failed ({e}); using faster-whisper output")

    segs = [{"start": s.start, "end": s.end, "text": s.text.strip()}
            for s in segments_iter]
    return lang, segs


def _sound_events(wav: Path, duration: float) -> list[dict]:
    """Significant non-speech sounds as [{start,end,label}]."""
    try:
        import numpy as np
        import librosa
        from panns_inference import SoundEventDetection, labels
    except Exception as e:
        log(f"  sound-event detection unavailable ({e}); skipping")
        return []

    audio, _ = librosa.load(str(wav), sr=32000, mono=True)
    audio = audio[None, :]
    sed = SoundEventDetection(checkpoint_path=None, device="cpu")
    framewise = sed.inference(audio)[0]            # (frames, classes)
    n_frames = framewise.shape[0]
    fps = n_frames / max(duration, 0.001)

    events = []
    import numpy as np
    for ci, label in enumerate(labels):
        if label in SED_IGNORE:
            continue
        active = framewise[:, ci] > SED_THRESHOLD
        if not active.any():
            continue
        # contiguous runs
        idx = np.where(active)[0]
        runs = np.split(idx, np.where(np.diff(idx) > 2)[0] + 1)
        for r in runs:
            if len(r) == 0:
                continue
            start, end = r[0] / fps, r[-1] / fps
            if end - start < SED_MIN_DURATION:
                continue
            peak = float(framewise[r, ci].max())
            events.append({"start": round(start, 2), "end": round(end, 2),
                           "label": label, "score": round(peak, 3)})
    # keep the strongest, non-trivial ones; sort by time
    events.sort(key=lambda e: e["score"], reverse=True)
    events = events[:12]
    events.sort(key=lambda e: e["start"])
    return events


def _fmt_ts(seconds: float, vtt: bool = False) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    sep = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _build_cues(segments: list[dict], sounds: list[dict]) -> list[dict]:
    cues = [{"start": s["start"], "end": s["end"], "text": s["text"]}
            for s in segments if s["text"]]
    for ev in sounds:
        cues.append({"start": ev["start"], "end": ev["end"],
                     "text": f"[lyd: {lyd_label(ev['label'])}]"})
    cues.sort(key=lambda c: c["start"])
    return cues


def _write_subs(stem_dir: Path, name: str, cues: list[dict]) -> None:
    srt = stem_dir / f"{name}.srt"
    vtt = stem_dir / f"{name}.vtt"
    with open(srt, "w") as f:
        for i, c in enumerate(cues, 1):
            f.write(f"{i}\n{_fmt_ts(c['start'])} --> {_fmt_ts(c['end'])}\n{c['text']}\n\n")
    with open(vtt, "w") as f:
        f.write("WEBVTT\n\n")
        for c in cues:
            f.write(f"{_fmt_ts(c['start'], True)} --> {_fmt_ts(c['end'], True)}\n{c['text']}\n\n")


def _ffprobe_duration(clip: Path) -> float:
    cp = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-of", "default=nw=1:nk=1", str(clip)])
    try:
        return float(cp.stdout.strip())
    except ValueError:
        return 0.0


def cmd_subtitles(args) -> None:
    if not have("ffmpeg") or not have("ffprobe"):
        die("ffmpeg/ffprobe not found on PATH. Install it yourself: brew install ffmpeg")
    if not args.no_asr:
        miss = missing_pypkgs(ASR_PYPKGS)
        if miss:
            die("speech transcription needs packages that aren't installed: "
                + ", ".join(miss) + "\nInstall them yourself (this skill won't):\n"
                f"  pip install {' '.join(miss)} --break-system-packages\n"
                "…or re-run with --no-asr to skip speech.")
    d = out_dir(args)
    clips_dir = d / "clips"
    subs_dir = d / "subtitles"
    subs_dir.mkdir(exist_ok=True)
    clips = load_json(d / "manifest.json")["clips"]

    for c in clips:
        clip = clips_dir / c["name"]
        if not clip.exists():
            log(f"skip {c['name']} (not downloaded)")
            continue
        stem = clip.stem
        tjson = subs_dir / f"{stem}.transcript.json"
        if tjson.exists() and not args.force:
            log(f"skip {c['name']} (already transcribed)")
            continue

        log(f"transcribing {c['name']}")
        wav = subs_dir / f"{stem}.wav"
        _extract_wav(clip, wav)
        duration = _ffprobe_duration(clip)

        lang, segments = ("", [])
        if not args.no_asr:
            lang, segments = _transcribe(wav)
        sounds = [] if args.no_sound_events else _sound_events(wav, duration)

        cues = _build_cues(segments, sounds)
        _write_subs(subs_dir, stem, cues)
        save_json(tjson, {
            "clip": c["name"], "language": lang, "duration": duration,
            "segments": segments, "sound_events": sounds,
        })
        wav.unlink(missing_ok=True)   # don't keep the scratch audio
        log(f"  lang={lang or '?'}  segments={len(segments)}  sounds={len(sounds)}")


# ----------------------------------------------------------------------------- #
# Stage: frames
# ----------------------------------------------------------------------------- #

def cmd_frames(args) -> None:
    if not have("ffmpeg") or not have("ffprobe"):
        die("ffmpeg/ffprobe not found on PATH.")
    d = out_dir(args)
    clips_dir = d / "clips"
    frames_root = d / "frames"
    frames_root.mkdir(exist_ok=True)
    clips = load_json(d / "manifest.json")["clips"]

    for c in clips:
        clip = clips_dir / c["name"]
        if not clip.exists():
            continue
        stem = clip.stem
        fdir = frames_root / stem
        fdir.mkdir(exist_ok=True)
        if any(fdir.glob("f*.jpg")) and not args.force:
            log(f"skip frames for {c['name']} (already sampled)")
            continue

        duration = _ffprobe_duration(clip)
        n = max(2, min(args.max_frames, int(duration // 10) + 1))
        # evenly spaced, avoiding the very start/end
        span = max(duration - 1.0, 0.1)
        times = [0.5 + span * i / (n - 1) for i in range(n)] if n > 1 else [duration / 2]
        log(f"sampling {n} frame(s) from {c['name']}")
        for i, t in enumerate(times, 1):
            # Fit inside a max-dim box, preserving aspect ratio, so vertical (9:16/
            # TikTok) and horizontal clips both come out sensibly sized. ffmpeg
            # auto-rotates by default, so rotated phone frames are upright.
            run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(clip),
                 "-frames:v", "1",
                 "-vf", f"scale=w={args.max_dim}:h={args.max_dim}:"
                        "force_original_aspect_ratio=decrease",
                 "-q:v", "3", str(fdir / f"f{i:02d}.jpg")], capture=True)


# ----------------------------------------------------------------------------- #
# Stage: catalogue
# ----------------------------------------------------------------------------- #

def _parse_capture_time(name: str, probe_tags: dict) -> str | None:
    mo = PXL_RE.search(name)
    if mo:
        ymd, hms = mo.group(1), mo.group(2)
        try:
            return datetime.strptime(ymd + hms, "%Y%m%d%H%M%S").isoformat()
        except ValueError:
            pass
    ct = probe_tags.get("creation_time")
    if ct:
        try:
            return datetime.fromisoformat(ct.replace("Z", "+00:00")).isoformat()
        except ValueError:
            return ct
    return None


def _parse_gps(tags: dict) -> dict | None:
    for k, v in tags.items():
        if "location" in k.lower() and isinstance(v, str):
            m = re.search(r"([+-]\d+\.?\d*)([+-]\d+\.?\d*)", v)
            if m:
                return {"lat": float(m.group(1)), "lon": float(m.group(2))}
    return None


def _ffprobe(clip: Path) -> dict:
    cp = run(["ffprobe", "-v", "error", "-print_format", "json",
              "-show_format", "-show_streams", str(clip)])
    try:
        return json.loads(cp.stdout)
    except json.JSONDecodeError:
        return {}


def _orientation(vstream: dict) -> tuple[int, int, str]:
    """Display width/height and orientation, accounting for rotation metadata.

    Phone clips (especially vertical/TikTok) store frames sideways with a rotation
    flag; the *displayed* size swaps when rotated 90/270. Returns (w, h, label) where
    label is 'vertical' | 'horizontal' | 'square' | 'unknown'.
    """
    w = int(vstream.get("width", 0) or 0)
    h = int(vstream.get("height", 0) or 0)
    rot = 0
    tags = vstream.get("tags", {}) or {}
    if "rotate" in tags:
        try:
            rot = abs(int(tags["rotate"])) % 360
        except ValueError:
            rot = 0
    for sd in vstream.get("side_data_list", []) or []:
        if "rotation" in sd:
            try:
                rot = abs(int(round(float(sd["rotation"])))) % 360
            except (ValueError, TypeError):
                pass
    if rot in (90, 270):
        w, h = h, w
    if not w or not h:
        label = "unknown"
    elif h > w:
        label = "vertical"
    elif w > h:
        label = "horizontal"
    else:
        label = "square"
    return w, h, label


def cmd_catalogue_build(args) -> None:
    d = out_dir(args)
    clips_dir = d / "clips"
    subs_dir = d / "subtitles"
    frames_root = d / "frames"
    manifest = load_json(d / "manifest.json")
    entries = []

    for c in manifest["clips"]:
        clip = clips_dir / c["name"]
        if not clip.exists():
            continue
        probe = _ffprobe(clip)
        fmt = probe.get("format", {})
        tags = fmt.get("tags", {}) or {}
        vstream = next((s for s in probe.get("streams", [])
                        if s.get("codec_type") == "video"), {})

        stem = clip.stem
        tjson = subs_dir / f"{stem}.transcript.json"
        transcript = load_json(tjson) if tjson.exists() else {}
        frames = sorted(str(p) for p in (frames_root / stem).glob("f*.jpg")) \
            if (frames_root / stem).exists() else []

        fr = vstream.get("r_frame_rate", "0/1")
        try:
            num, den = fr.split("/")
            fps = round(float(num) / float(den), 2) if float(den) else None
        except Exception:
            fps = None

        disp_w, disp_h, orient = _orientation(vstream)

        entries.append({
            "filename": c["name"],
            "remote_path": c["remote_path"],
            "local_path": str(clip),
            "capture_time": _parse_capture_time(c["name"], tags),
            "duration_s": round(float(fmt.get("duration", 0) or 0), 2),
            "resolution": f"{disp_w}x{disp_h}" if disp_w and disp_h else "?",
            "orientation": orient,
            "fps": fps,
            "gps": _parse_gps(tags),
            "language": transcript.get("language"),
            "transcript": transcript.get("segments", []),
            "sound_events": transcript.get("sound_events", []),
            "frames": frames,
            "visual": "",     # Claude fills this from the frames
            "summary": "",    # Claude fills this (Nynorsk)
        })

    entries.sort(key=lambda e: e["capture_time"] or e["filename"])
    save_json(d / "clips.json", {"date": manifest["date"], "clips": entries})
    _render_md(d)
    log(f"built clips.json with {len(entries)} clip(s). "
        f"Now view frames/<clip>/ and fill 'visual' + 'summary' in clips.json, "
        f"then run catalogue-render.")


def _render_md(d: Path) -> None:
    data = load_json(d / "clips.json")
    lines = [f"# Klippkatalog — {data['date']}", ""]
    lines.append(f"_{len(data['clips'])} klipp. Generert {datetime.now():%Y-%m-%d %H:%M}._")
    lines.append("")
    for i, c in enumerate(data["clips"], 1):
        t = c["capture_time"] or "?"
        hhmm = t[11:16] if len(t) >= 16 else t
        lines.append(f"## {i}. {hhmm} — `{c['filename']}`")
        meta = [f"{c['duration_s']:.0f}s", c["resolution"]]
        if c.get("orientation") and c["orientation"] != "unknown":
            meta.append({"vertical": "▯ vertikal", "horizontal": "▭ horisontal",
                         "square": "▢ kvadratisk"}.get(c["orientation"], c["orientation"]))
        if c.get("fps"):
            meta.append(f"{c['fps']}fps")
        if c.get("language"):
            meta.append(f"språk: {c['language']}")
        if c.get("gps"):
            meta.append(f"GPS {c['gps']['lat']:.4f},{c['gps']['lon']:.4f}")
        lines.append("`" + "  ·  ".join(meta) + "`")
        lines.append("")
        if c.get("summary"):
            lines.append(f"**{c['summary']}**")
            lines.append("")
        if c.get("visual"):
            lines.append(c["visual"])
            lines.append("")
        if c.get("sound_events"):
            labs = ", ".join(sorted({lyd_label(e["label"]) for e in c["sound_events"]}))
            lines.append(f"*Lydar:* {labs}")
            lines.append("")
        if c.get("transcript"):
            text = " ".join(s["text"] for s in c["transcript"]).strip()
            if text:
                snippet = text if len(text) <= 400 else text[:400] + "…"
                lines.append(f"> {snippet}")
                lines.append("")
        lines.append(f"<sub>srt: `subtitles/{Path(c['filename']).stem}.srt`</sub>")
        lines.append("")
    with open(d / "catalogue.md", "w") as f:
        f.write("\n".join(lines))


def cmd_catalogue_render(args) -> None:
    d = out_dir(args)
    _render_md(d)
    log(f"rendered {d/'catalogue.md'}")


# ----------------------------------------------------------------------------- #
# Stage: doctor (environment check — never installs anything)
# ----------------------------------------------------------------------------- #

def cmd_doctor(args) -> None:
    log("Environment check. This skill never installs anything — if something is")
    log("missing, run the command shown and install it yourself.\n")

    ok = True
    for b in REQUIRED_BINARIES:
        present = have(b)
        ok = ok and present
        log(f"  [{'ok ' if present else 'MISS'}] {b}")
    miss = missing_pypkgs(REQUIRED_PYPKGS)
    for mod, pip_name in REQUIRED_PYPKGS.items():
        log(f"  [{'ok ' if pip_name not in miss else 'MISS'}] python: {pip_name}")

    log("")
    if not have("ffmpeg") or not have("ffprobe"):
        log("  → ffmpeg:   brew install ffmpeg")
    if not have("jotta-cli"):
        log("  → jotta-cli: install per Jottacloud docs, then `jotta-cli login`")
    if miss:
        ok = False
        log("  → python:   pip install " + " ".join(miss) + " --break-system-packages")

    log("")
    if ok:
        log("All good — ready to run the pipeline.")
    else:
        log("Install the missing pieces above, then re-run `doctor`.")
        sys.exit(1)


# ----------------------------------------------------------------------------- #
# CLI
# ----------------------------------------------------------------------------- #

def main() -> None:
    p = argparse.ArgumentParser(description="jotta-clip-catalogue pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_out(sp):
        sp.add_argument("--out", required=True, help="working folder for this date")

    sp = sub.add_parser("discover")
    add_out(sp)
    sp.add_argument("--date", required=True, help="YYYY-MM-DD")
    sp.add_argument("--mode", choices=["album", "auto", "both"], default="both")
    sp.add_argument("--album", default=None, help="album name (for album/both mode)")
    sp.add_argument("--source", choices=["pixel", "all"], default="pixel")
    sp.set_defaults(func=cmd_discover)

    sp = sub.add_parser("fetch")
    add_out(sp)
    sp.add_argument("--timeout", type=int, default=3600, help="seconds to wait")
    sp.add_argument("--poll", type=int, default=10, help="poll interval seconds")
    sp.set_defaults(func=cmd_fetch)

    sp = sub.add_parser("subtitles")
    add_out(sp)
    sp.add_argument("--no-asr", action="store_true")
    sp.add_argument("--no-sound-events", action="store_true")
    sp.add_argument("--force", action="store_true", help="re-do clips already done")
    sp.set_defaults(func=cmd_subtitles)

    sp = sub.add_parser("frames")
    add_out(sp)
    sp.add_argument("--max-frames", type=int, default=6)
    sp.add_argument("--max-dim", type=int, default=768,
                    help="longest frame side in px (fits both orientations)")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_frames)

    sp = sub.add_parser("catalogue-build")
    add_out(sp)
    sp.set_defaults(func=cmd_catalogue_build)

    sp = sub.add_parser("catalogue-render")
    add_out(sp)
    sp.set_defaults(func=cmd_catalogue_render)

    sp = sub.add_parser("doctor")
    sp.set_defaults(func=cmd_doctor)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
