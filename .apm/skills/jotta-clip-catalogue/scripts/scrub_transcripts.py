#!/usr/bin/env python3
"""Remove hallucinated Whisper segments from transcript.json + srt/vtt.

Whisper models hallucinate on ambient noise (train rumble, wind, room tone):
YouTube-outro boilerplate, film-credit lines, and a stock of stereotyped phrases.
NB-Whisper's favourites are «Hva er det du gjør?» / «Hva gjør du?» on engine
noise. These pollute the catalogue and mislead the editor.

IMPORTANT for Claude: run without --apply first (dry run), show the user what
would be removed, and get a yes before applying. Keep ambiguous real-sounding
exclamations («Fy faen.», «Seriøst.») — they are often genuine. Genuine PA
announcements and conductor speech must survive; if a real announcement shares a
file with garbage, only the garbage segments go.

  python3 scrub_transcripts.py --out DIR              # dry run, lists hits
  python3 scrub_transcripts.py --out DIR --apply      # rewrite transcript+srt/vtt
  ... --extra-pattern 'regex' (repeatable) for session-specific garbage
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_PATTERNS = [
    r"^\W*$",                                  # punctuation-only segments
    r"hva (er det\s*)?(deta?\s*)?(gj\s*)?(det\s*)?du gjør",
    r"^hva\?*$", r"hva gjør\??",
    r"terima kasih", r"субтитры", r"dimatorzok",
    r"thanks? for watching", r"takk for at du så",
    r"tekstet av nicolai winther",
    r"enhver likhet med virkelige",
    r"undertekster av", r"subtitles by",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--extra-pattern", action="append", default=[])
    a = ap.parse_args()
    out = Path(a.out).expanduser()

    for cand in (Path(__file__).resolve().parent, out):
        if (cand / "pipeline.py").exists():
            sys.path.insert(0, str(cand))
            break
    import pipeline

    pat = re.compile("|".join(DEFAULT_PATTERNS + a.extra_pattern), re.IGNORECASE)
    subs = out / "subtitles"
    removed_total = 0
    for tj in sorted(subs.glob("*.transcript.json")):
        data = json.loads(tj.read_text())
        segs = data.get("segments", [])
        bad = [s for s in segs if pat.search(s["text"].strip())]
        if not bad:
            continue
        removed_total += len(bad)
        stem = tj.name.replace(".transcript.json", "")
        for s in bad:
            print(f"  {stem}: [{s['start']:.1f}s] {s['text']!r}")
        if a.apply:
            keep = [s for s in segs if s not in bad]
            data["segments"] = keep
            if not keep:
                data["language"] = None
            cues = pipeline._build_cues(keep, data.get("sound_events", []))
            pipeline._write_subs(subs, stem, cues)
            tj.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    verb = "removed" if a.apply else "would remove"
    print(f"{verb} {removed_total} segment(s)."
          + ("" if a.apply else "  Re-run with --apply to do it."))


if __name__ == "__main__":
    main()
