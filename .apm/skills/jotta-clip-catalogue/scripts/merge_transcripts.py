#!/usr/bin/env python3
"""Fold subtitles/*.transcript.json into clips.json WITHOUT touching visual/summary.

Why: `pipeline.py catalogue-build` rebuilds clips.json from scratch, wiping the
visual descriptions and Nynorsk summaries Claude filled in. When transcripts or
sound events arrive (or change — sound_pass, scrubbing) AFTER step 6, use this
instead of re-running catalogue-build, then `pipeline.py catalogue-render`.

  python3 merge_transcripts.py --out DIR
"""
import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).expanduser()

    cat = json.loads((out / "clips.json").read_text())
    n = 0
    for c in cat["clips"]:
        stem = Path(c["filename"]).stem
        tj = out / "subtitles" / f"{stem}.transcript.json"
        if not tj.exists():
            continue
        t = json.loads(tj.read_text())
        c["language"] = t.get("language")
        c["transcript"] = t.get("segments", [])
        c["sound_events"] = t.get("sound_events", [])
        n += 1
    (out / "clips.json").write_text(json.dumps(cat, indent=2,
                                               ensure_ascii=False))
    print(f"merged {n} transcript(s) into clips.json "
          f"(visual/summary untouched). Now run catalogue-render.")


if __name__ == "__main__":
    main()
