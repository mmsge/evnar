#!/usr/bin/env python3
"""Build manifest.json from clips that are ALREADY on disk (skip discover/fetch).

Use when the day's clips were downloaded earlier (or arrived some other way) and
live in a folder. Writes manifest.json in the pipeline's schema and symlinks the
videos into <out>/clips/ — the layout every later stage expects — without moving
or copying the originals.

  python3 local_manifest.py --out ~/videos/siste-strekket --date 2026-06-05 \
      [--album "Album name"] [--source pixel|all]
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".m4v"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--album", default=None)
    ap.add_argument("--source", default="pixel", choices=["pixel", "all"])
    a = ap.parse_args()

    d = Path(a.out).expanduser()
    compact = a.date.replace("-", "")
    clips = []
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in VIDEO_EXT or not f.is_file():
            continue
        if a.source == "pixel" and not f.name.upper().startswith("PXL_"):
            continue
        if f.name.upper().startswith("PXL_") and compact not in f.name:
            continue
        st = f.stat()
        clips.append({
            "name": f.name,
            "remote_path": (f"/Photos/Albums/{a.album}/{f.name}" if a.album
                            else f"local:{f}"),
            "size": st.st_size,
            "modified": int(st.st_mtime),
        })
    if not clips:
        raise SystemExit("no matching video files found in --out")

    (d / "manifest.json").write_text(json.dumps({
        "date": a.date, "mode": "local", "album": a.album,
        "source": a.source,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "clips": clips,
    }, indent=2, ensure_ascii=False))

    clips_dir = d / "clips"
    clips_dir.mkdir(exist_ok=True)
    for c in clips:
        link = clips_dir / c["name"]
        if not link.exists():
            link.symlink_to(Path("..") / c["name"])
    print(f"{len(clips)} clip(s) -> manifest.json; symlinked into clips/")


if __name__ == "__main__":
    main()
