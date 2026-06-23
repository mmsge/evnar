#!/usr/bin/env python3
"""Second pass: add PANNs sound events to clips whose transcript.json has none.

Why this exists: panns_inference fetches its model files with `wget`, which macOS
does not ship. The first subtitles run then writes perfectly good speech
transcripts but zero sound events. Rather than re-transcribing everything with
--force, this script redoes ONLY the sound-event detection and merges the result
into the existing transcript.json + srt/vtt.

One-time prep on the Mac (the two files panns_inference would have wget'ed):

  mkdir -p ~/panns_data
  curl -L -o ~/panns_data/class_labels_indices.csv \
    'http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv'
  curl -L -o ~/panns_data/Cnn14_DecisionLevelMax.pth \
    'https://zenodo.org/record/3987831/files/Cnn14_DecisionLevelMax_mAP%3D0.385.pth?download=1'

Then:  python3 sound_pass.py --out ~/videos/<day-folder>
(Needs pipeline.py importable: same folder as this script, or in the out folder.)
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

    clips_dir, subs = out / "clips", out / "subtitles"
    todo = []
    for tj in sorted(subs.glob("*.transcript.json")):
        data = json.loads(tj.read_text())
        if not data.get("sound_events"):
            todo.append((tj, data))
    print(f"{len(todo)} clip(s) need sound events")

    for tj, data in todo:
        stem = tj.name.replace(".transcript.json", "")
        clip = clips_dir / f"{stem}.mp4"
        if not clip.exists():
            print(f"skip {stem} (clip missing)")
            continue
        print(f"sound events for {stem}")
        wav = subs / f"{stem}.wav"
        pipeline._extract_wav(clip, wav)
        duration = data.get("duration") or pipeline._ffprobe_duration(clip)
        sounds = pipeline._sound_events(wav, duration)
        wav.unlink(missing_ok=True)
        if not sounds:
            print("  none detected")
            continue
        data["sound_events"] = sounds
        cues = pipeline._build_cues(data.get("segments", []), sounds)
        pipeline._write_subs(subs, stem, cues)
        tj.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"  {len(sounds)} event(s): "
              + ", ".join(sorted({s['label'] for s in sounds})))


if __name__ == "__main__":
    main()
