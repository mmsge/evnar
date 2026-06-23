#!/usr/bin/env python3
"""Editorial phase 3: render an edit decision table into Resolve-ready files.

Reads <out>/evidence.json plus an edit.json decision table (which Claude writes
after the editorial reasoning pass) and produces, in <out>/:

  <name>.otio            timeline: V1 + mirrored A1, track markers with notes
  <name>.locations.srt   place-name caption per event, in OUTPUT (cut) time
  <name>.sound.srt       every speech + [lyd: …] cue from the included ranges,
                         clipped to in/out and shifted to OUTPUT time

No opentimelineio dependency: the OTIO JSON schema (Timeline.1/Stack.1/Track.1/
Clip.1/ExternalReference.1/Marker.2) is written directly — DaVinci Resolve
imports it via Timelines > Import. Non-destructive: file:// references to the
source media; nothing is re-encoded or moved.

edit.json schema:
{
  "name": "edit_v2",
  "timeline_rate": 30,
  "media_dir": "/Users/markus/videos/<day-folder>",   // ABSOLUTE host path
  "events": [
    {"stem": "PXL_20260605_142337007", "in": 26.0, "out": 36.0,
     "colour": "PURPLE", "note": "OPNAR/hook: …"}
  ],
  "dropped":      [{"stem": "…", "why": "…"}],
  "setup_payoff": [{"setup": "…", "payoff": "…"}]
}
Marker colours: PINK RED ORANGE YELLOW GREEN CYAN BLUE PURPLE MAGENTA BLACK WHITE.

  python3 build_edit.py --out DIR [--edit DIR/edit.json]
"""
import argparse
import json
from pathlib import Path

try:
    from labels_nn import lyd_label
except ImportError:
    def lyd_label(label):
        return label.lower()


def rt(value, rate):
    return {"OTIO_SCHEMA": "RationalTime.1", "rate": rate, "value": value}


def trange(start_f, dur_f, rate):
    return {"OTIO_SCHEMA": "TimeRange.1",
            "start_time": rt(start_f, rate), "duration": rt(dur_f, rate)}


def make_clip(media_dir, stem, in_s, out_s, dur_s, fps):
    return {"OTIO_SCHEMA": "Clip.1", "name": stem,
            "source_range": trange(round(in_s * fps),
                                   round((out_s - in_s) * fps), fps),
            "media_reference": {
                "OTIO_SCHEMA": "ExternalReference.1", "name": f"{stem}.mp4",
                "target_url": f"file://{media_dir}/{stem}.mp4",
                "available_range": trange(0, round(dur_s * fps), fps),
                "metadata": {}},
            "markers": [], "effects": [], "metadata": {}}


def srt_ts(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--edit", default=None)
    a = ap.parse_args()
    out = Path(a.out).expanduser()
    edit = json.loads(Path(a.edit or out / "edit.json").expanduser().read_text())
    ev = {Path(c["filename"]).stem: c
          for c in json.loads((out / "evidence.json").read_text())["clips"]}

    name, tl_rate = edit["name"], float(edit.get("timeline_rate", 30))
    media_dir = edit["media_dir"].rstrip("/")
    v1, a1, markers, loc_lines, cues = [], [], [], [], []
    t = 0.0
    for i, evt in enumerate(edit["events"], 1):
        e = ev[evt["stem"]]
        fps = e["fps"] or tl_rate
        in_s, out_s = evt["in"], min(evt["out"], e["duration_s"])
        v1.append(make_clip(media_dir, evt["stem"], in_s, out_s,
                            e["duration_s"], fps))
        a1.append(make_clip(media_dir, evt["stem"], in_s, out_s,
                            e["duration_s"], fps))
        markers.append({"OTIO_SCHEMA": "Marker.2",
                        "name": f"{i:02d} {e.get('place') or evt['stem']}",
                        "color": evt.get("colour", "GREEN"),
                        "marked_range": trange(round(t * tl_rate), 1, tl_rate),
                        "metadata": {"note": evt.get("note", "")}})
        dur = out_s - in_s
        if e.get("place"):
            loc_lines += [str(len(loc_lines) // 4 + 1),
                          f"{srt_ts(t)} --> {srt_ts(t + min(4.0, dur))}",
                          e["place"], ""]
        raw = [(s["start"], s["end"], s["text"]) for s in e["speech"]]
        raw += [(s["start"], s["end"], f"[lyd: {lyd_label(s['label'])}]")
                for s in e["sound_events"]]
        for cs, ce, text in raw:
            if ce <= in_s or cs >= out_s:
                continue
            cs2, ce2 = max(cs, in_s), min(ce, out_s)
            if ce2 - cs2 >= 0.15:
                cues.append((t + cs2 - in_s, t + ce2 - in_s, text))
        t += dur

    def track(kind, children, mk):
        return {"OTIO_SCHEMA": "Track.1", "name": kind[0] + "1", "kind": kind,
                "source_range": None, "markers": mk, "effects": [],
                "metadata": {}, "children": children}

    tl = {"OTIO_SCHEMA": "Timeline.1", "name": name,
          "global_start_time": rt(0, tl_rate),
          "metadata": {"generator": "build_edit.py"},
          "tracks": {"OTIO_SCHEMA": "Stack.1", "name": "tracks",
                     "source_range": None, "metadata": {}, "markers": [],
                     "effects": [],
                     "children": [track("Video", v1, markers),
                                  track("Audio", a1, [])]}}
    (out / f"{name}.otio").write_text(json.dumps(tl, indent=2,
                                                 ensure_ascii=False))
    (out / f"{name}.locations.srt").write_text("\n".join(loc_lines) + "\n")
    cues.sort(key=lambda c: c[0])
    lines = []
    for i, (cs, ce, text) in enumerate(cues, 1):
        lines += [str(i), f"{srt_ts(cs)} --> {srt_ts(ce)}", text, ""]
    (out / f"{name}.sound.srt").write_text("\n".join(lines) + "\n")

    print(f"== {name}: {len(edit['events'])} events, total "
          f"{int(t // 60)}:{t % 60:04.1f} ==")
    pos = 0.0
    for i, evt in enumerate(edit["events"], 1):
        e = ev[evt["stem"]]
        dur = min(evt["out"], e["duration_s"]) - evt["in"]
        print(f"{i:02d}  {srt_ts(pos)[:8]}  {evt['stem']}  "
              f"[{evt['in']:6.1f}-{min(evt['out'], e['duration_s']):6.1f}]  "
              f"{evt.get('note', '').split('.')[0]}.")
        pos += dur
    for sp in edit.get("setup_payoff", []):
        print(f"  setup: {sp['setup']}\n    -> payoff: {sp['payoff']}")
    for d in edit.get("dropped", []):
        print(f"  dropped {d['stem']}: {d['why']}")
    print(f"sound cues: {len(cues)}; location captions: {len(loc_lines) // 4}")


if __name__ == "__main__":
    main()
