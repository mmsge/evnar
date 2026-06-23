#!/usr/bin/env python3
"""Editorial phase 1: build evidence.json — the per-clip fact layer for a cut.

Folds together, per clip: duration/fps/orientation/GPS (from clips.json), speech
segments + first-speech time (scrubbed transcripts), sound events, sampled frame
paths with their SOURCE timestamps (recomputed with the same maths pipeline.py
used, so they match the jpgs), face counts per frame (OpenCV Haar if available),
and the visual/summary Claude already wrote for the catalogue.

Place names: offline reverse-geocoders are usually unavailable, and Claude is a
perfectly good geocoder. Pass --places places.json ({"<stem>": "Voss", ...}) —
Claude writes that mapping by reading the GPS coordinates in clips.json. Clips
absent from the mapping get place=null (report them).

  python3 build_evidence.py --out DIR [--places places.json]
"""
import argparse
import json
from pathlib import Path


def frame_times(duration: float, n: int) -> list:
    span = max(duration - 1.0, 0.1)
    return [0.5 + span * i / (n - 1) for i in range(n)] if n > 1 else [duration / 2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--places", default=None)
    a = ap.parse_args()
    out = Path(a.out).expanduser()

    places = (json.loads(Path(a.places).expanduser().read_text())
              if a.places else {})
    cascade = None
    try:
        import cv2
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    except Exception:
        pass

    cat = json.loads((out / "clips.json").read_text())
    rows, no_place = [], []
    for c in cat["clips"]:
        stem = Path(c["filename"]).stem
        jpgs = sorted((out / "frames" / stem).glob("f*.jpg"))
        frames = []
        for jpg, t in zip(jpgs, frame_times(c["duration_s"], len(jpgs))):
            n = None
            if cascade is not None:
                import cv2
                img = cv2.imread(str(jpg))
                if img is not None:
                    n = len(cascade.detectMultiScale(
                        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                        scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)))
            frames.append({"file": f"frames/{stem}/{jpg.name}",
                           "t": round(t, 2), "faces": n})
        speech = c.get("transcript", [])
        place = places.get(stem)
        if place is None:
            no_place.append(stem)
        rows.append({
            "filename": c["filename"], "capture_time": c["capture_time"],
            "duration_s": c["duration_s"], "fps": c["fps"],
            "orientation": c["orientation"], "gps": c["gps"], "place": place,
            "speech": speech,
            "first_speech_s": speech[0]["start"] if speech else None,
            "sound_events": c.get("sound_events", []),
            "frames": frames,
            "visual": c.get("visual", ""), "summary": c.get("summary", ""),
        })
    (out / "evidence.json").write_text(json.dumps(
        {"date": cat["date"], "clips": rows}, indent=2, ensure_ascii=False))
    print(f"evidence.json: {len(rows)} clips"
          + (f"; no place name for: {', '.join(no_place)}" if no_place else ""))


if __name__ == "__main__":
    main()
