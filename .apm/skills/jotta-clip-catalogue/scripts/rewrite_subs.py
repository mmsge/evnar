#!/usr/bin/env python3
"""Regenerate every srt/vtt from transcript.json.

Run after editing transcript.json segments by hand — e.g. the nynorskifisering
pass (bokmål ASR-text -> nynorsk, «[På engelsk] …»-prefiks på framandspråk) —
or to re-render cues with updated nynorsk sound labels.

  python3 rewrite_subs.py --out DIR
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).expanduser()

    for cand in (Path(__file__).resolve().parent, out):
        if (cand / "pipeline.py").exists():
            sys.path.insert(0, str(cand))
            break
    import pipeline

    subs = out / "subtitles"
    n = 0
    for tj in sorted(subs.glob("*.transcript.json")):
        data = json.loads(tj.read_text())
        stem = tj.name.replace(".transcript.json", "")
        cues = pipeline._build_cues(data.get("segments", []),
                                    data.get("sound_events", []))
        pipeline._write_subs(subs, stem, cues)
        n += 1
    print(f"rewrote srt/vtt for {n} clip(s)")
    try:
        import labels_nn
        if labels_nn.unmapped():
            print("labels missing a nynorsk mapping (extend labels_nn.LYD_NN):")
            for lab in labels_nn.unmapped():
                print(f"  - {lab}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
