"""
Carousel PDF generator for Markus's LinkedIn posts — "Bolk" green theme.

Renders a multi-page 4:5 PDF (native 1080x1350 LinkedIn carousel size) from a
JSON config, using HTML/CSS rendered by wkhtmltopdf (a real WebKit engine). No
browser download required, works offline.

Look: deep forest-green canvas, lime accent (progress bar + kicker underline +
icon strokes), large white Lato Black headlines that fill the page, optional
light cream cards for content, built-in outlined line-icons, image-forward
slides. Footer with "project · note" + page counter.

Usage:
    python3 build_carousel.py <config.json> [--out path/to/output.pdf]

Config schema (see assets/example_config.json):

{
  "project": "Project Name · open source",
  "out": "name-of-output.pdf",
  "footnote": "personleg notat",          // optional, footer right of project
  "slides": [
    {
      "kicker": "EI LITA HISTORIE",
      "title": "Heading text\\nwith\\nmanual line breaks.",
      "sub": "Optional subtitle. Can also have \\n breaks.",
      "title_size": 118,                   // optional px override
      "visual": { "type": "...", ... }
    }
  ]
}

Supported visual types:
  - {"type": "none"}                      text-only slide (headline carries it)
  - {"type": "image", "path": "...", "mode": "halfpage|fullbleed|contained",
       "caption": "..."}                   photo. Default mode = halfpage.
  - {"type": "icon", "name": "notes", "pos": "right|center", "frame": false}
       big outlined line-icon (see ICONS for names)
  - {"type": "checklist", "header": "Oppfolgingar", "sub": "...",
       "items": [{"text": "...", "done": true}, ...]}   cream checklist card
  - {"type": "step_cards", "cards": [{"label","title","sub"}, ...], "arrows": true}
  - {"type": "stat_cards", "cards": [{"big","line1","line2","color"}, ...]}
       color: lime | white | cream | mute (tints the big number)
  - {"type": "url_cta", "label": "...", "url": "...", "lines": ["...", ...],
       "cta": "-> ..."}                    closing panel (Bolk p4 style)
  - {"type": "sankey", "data_path": "...", "years": [...], "threshold": 0.5,
       "caption": "..."}                   multi-stage flow on a light card
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

# ---------------------------------------------------------------------------
# Theme  (Bolk)
# ---------------------------------------------------------------------------

BG = "#143521"          # deep forest-green page
BG_PANEL = "#1c4a2d"    # lighter green inset panel / cards on dark
SEG_OFF = "#2d5a3c"     # unfilled progress segment
PANEL_LINE = "#2f5a3e"  # hairline on dark panels
LIME = "#9fe822"        # chartreuse accent
WHITE = "#ffffff"
SUB = "#bcd2bb"         # muted pale-green body on dark
KICKER = "#d6ecca"      # pale kicker label
FOOT = "#6f8c74"        # muted footer
CREAM = "#f1ede2"       # light card background (legacy beige lives here)
CREAM_LINE = "#ddd6c4"  # hairline on cream
INK = "#10301d"         # dark ink on cream
INK_BODY = "#41513f"    # muted body on cream
INK_MUTE = "#8a9485"    # faint label on cream

STAT_COLORS = {"lime": LIME, "white": WHITE, "cream": CREAM, "mute": SUB}

# Native LinkedIn carousel size (4:5). Designing here keeps output crisp.
W = 1080
H = 1350
MARGIN = 84

# ---------------------------------------------------------------------------
# Built-in line-icons. viewBox 0 0 100 100. {S}=structure stroke (white),
# {A}=accent stroke (lime), {W}=stroke width. Round caps/joins.
# ---------------------------------------------------------------------------

ICONS = {
    "notes": (
        '<rect x="20" y="10" width="60" height="80" rx="10" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<line x1="34" y1="36" x2="66" y2="36" stroke="{A}" stroke-width="{W}" stroke-linecap="round"/>'
        '<line x1="34" y1="50" x2="66" y2="50" stroke="{A}" stroke-width="{W}" stroke-linecap="round"/>'
        '<line x1="34" y1="64" x2="54" y2="64" stroke="{A}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "train": (
        '<rect x="24" y="14" width="52" height="58" rx="12" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<line x1="24" y1="42" x2="76" y2="42" stroke="{S}" stroke-width="{W}"/>'
        '<circle cx="38" cy="57" r="4" fill="{A}"/><circle cx="62" cy="57" r="4" fill="{A}"/>'
        '<line x1="34" y1="78" x2="24" y2="90" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
        '<line x1="66" y1="78" x2="76" y2="90" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "map": (
        '<path d="M50 14 C34 14 22 26 22 42 C22 62 50 86 50 86 C50 86 78 62 78 42 C78 26 66 14 50 14 Z" fill="none" stroke="{S}" stroke-width="{W}" stroke-linejoin="round"/>'
        '<circle cx="50" cy="42" r="11" fill="none" stroke="{A}" stroke-width="{W}"/>'
    ),
    "code": (
        '<rect x="14" y="20" width="72" height="60" rx="10" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<polyline points="38,42 28,52 38,62" fill="none" stroke="{A}" stroke-width="{W}" stroke-linecap="round" stroke-linejoin="round"/>'
        '<polyline points="62,42 72,52 62,62" fill="none" stroke="{A}" stroke-width="{W}" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="54" y1="38" x2="46" y2="66" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "chart": (
        '<line x1="20" y1="84" x2="84" y2="84" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
        '<rect x="28" y="52" width="13" height="32" rx="3" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<rect x="49" y="36" width="13" height="48" rx="3" fill="{A}" stroke="none"/>'
        '<rect x="70" y="22" width="13" height="62" rx="3" fill="none" stroke="{S}" stroke-width="{W}"/>'
    ),
    "database": (
        '<ellipse cx="50" cy="24" rx="28" ry="11" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<path d="M22 24 V50 C22 56 35 61 50 61 C65 61 78 56 78 50 V24" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<path d="M22 50 V76 C22 82 35 87 50 87 C65 87 78 82 78 76 V50" fill="none" stroke="{A}" stroke-width="{W}"/>'
    ),
    "broadcast": (
        '<circle cx="34" cy="66" r="6" fill="{A}"/>'
        '<path d="M34 50 C43 50 50 57 50 66" fill="none" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
        '<path d="M34 36 C51 36 64 49 64 66" fill="none" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
        '<path d="M34 22 C58 22 78 42 78 66" fill="none" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "book": (
        '<path d="M50 26 C42 20 30 18 20 20 V76 C30 74 42 76 50 82 C58 76 70 74 80 76 V20 C70 18 58 20 50 26 Z" fill="none" stroke="{S}" stroke-width="{W}" stroke-linejoin="round"/>'
        '<line x1="50" y1="26" x2="50" y2="82" stroke="{A}" stroke-width="{W}"/>'
    ),
    "mic": (
        '<rect x="40" y="14" width="20" height="40" rx="10" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<path d="M28 46 C28 64 40 70 50 70 C60 70 72 64 72 46" fill="none" stroke="{A}" stroke-width="{W}" stroke-linecap="round"/>'
        '<line x1="50" y1="70" x2="50" y2="86" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "bulb": (
        '<path d="M34 56 C26 48 26 34 36 26 C46 18 60 20 67 30 C73 39 70 50 64 56 C61 59 60 62 60 66 H40 C40 62 38 60 34 56 Z" fill="none" stroke="{S}" stroke-width="{W}" stroke-linejoin="round"/>'
        '<line x1="42" y1="74" x2="58" y2="74" stroke="{A}" stroke-width="{W}" stroke-linecap="round"/>'
        '<line x1="44" y1="82" x2="56" y2="82" stroke="{A}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "gear": (
        '<circle cx="50" cy="50" r="13" fill="none" stroke="{A}" stroke-width="{W}"/>'
        '<path d="M50 14 v10 M50 76 v10 M14 50 h10 M76 50 h10 M25 25 l7 7 M68 68 l7 7 M75 25 l-7 7 M32 68 l-7 7" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "check": (
        '<rect x="24" y="16" width="52" height="68" rx="10" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<rect x="40" y="10" width="20" height="12" rx="4" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<polyline points="36,46 45,55 64,36" fill="none" stroke="{A}" stroke-width="{W}" stroke-linecap="round" stroke-linejoin="round"/>'
        '<line x1="36" y1="68" x2="64" y2="68" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
    ),
    "globe": (
        '<circle cx="50" cy="50" r="34" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<ellipse cx="50" cy="50" rx="15" ry="34" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<line x1="18" y1="40" x2="82" y2="40" stroke="{A}" stroke-width="{W}"/>'
        '<line x1="18" y1="60" x2="82" y2="60" stroke="{A}" stroke-width="{W}"/>'
    ),
    "calendar": (
        '<rect x="18" y="22" width="64" height="60" rx="10" fill="none" stroke="{S}" stroke-width="{W}"/>'
        '<line x1="18" y1="40" x2="82" y2="40" stroke="{S}" stroke-width="{W}"/>'
        '<line x1="34" y1="14" x2="34" y2="28" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
        '<line x1="66" y1="14" x2="66" y2="28" stroke="{S}" stroke-width="{W}" stroke-linecap="round"/>'
        '<circle cx="38" cy="56" r="5" fill="{A}"/><circle cx="58" cy="56" r="5" fill="{A}"/>'
    ),
}


def icon_svg(name: str, size: int, stroke: str = WHITE, accent: str = LIME,
             width: float = 6.0) -> str:
    inner = ICONS.get(name)
    if inner is None:
        raise ValueError(f"unknown icon: {name!r}. Available: {', '.join(sorted(ICONS))}")
    inner = inner.replace("{S}", stroke).replace("{A}", accent).replace("{W}", str(width))
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" '
            f'fill="none" xmlns="http://www.w3.org/2000/svg">{inner}</svg>')


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def image_data_uri(path: str) -> str:
    """Embed an image as a base64 data URI. wkhtmltopdf loads file:// background
    images unreliably; data URIs always render."""
    import base64
    p = Path(path)
    ext = p.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif",
            "webp": "webp"}.get(ext, "jpeg")
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{b64}"


def esc(s) -> str:
    return html.escape(str(s), quote=False)


def br(s: str) -> str:
    return esc(s).replace("\n", "<br>")


def font_face_css(fonts_dir: Path) -> str:
    """Emit @font-face rules only for Lato weights actually present, so the
    skill renders correctly wherever the TTFs are bundled and degrades cleanly
    (to the system sans stack) where they are not."""
    weights = {"Lato-Black.ttf": 900, "Lato-Bold.ttf": 700, "Lato-Regular.ttf": 400}
    rules = []
    for fname, weight in weights.items():
        f = fonts_dir / fname
        if f.exists():
            rules.append(
                "@font-face{font-family:'Lato';font-style:normal;"
                f"font-weight:{weight};src:url('file://{f.resolve()}') format('truetype');}}"
            )
    return "\n".join(rules)


def progress_html(index: int, total: int) -> str:
    pad = MARGIN
    gap = 16
    seg_w = (W - 2 * pad - gap * (total - 1)) / total
    segs = []
    for i in range(total):
        x = pad + i * (seg_w + gap)
        color = LIME if i < index else SEG_OFF
        segs.append(
            f'<div style="position:absolute;left:{x:.1f}px;top:78px;width:{seg_w:.1f}px;'
            f'height:12px;background:{color};border-radius:6px;"></div>'
        )
    return "".join(segs)


def heading_html(kicker: str, title: str, sub, title_size: int,
                 on_dark: bool = True) -> str:
    ink = WHITE if on_dark else INK
    sub_col = SUB if on_dark else INK_BODY
    kick_col = KICKER if on_dark else INK_MUTE
    parts = []
    if kicker:
        parts.append(
            f'<div style="font-size:23px;font-weight:700;letter-spacing:6px;'
            f'color:{kick_col};text-transform:uppercase;">{esc(kicker)}</div>'
            f'<div style="width:64px;height:8px;background:{LIME};border-radius:4px;'
            f'margin-top:14px;"></div>'
        )
    parts.append(
        f'<div style="font-family:\'Lato\',Arial,sans-serif;font-weight:900;'
        f'font-size:{title_size}px;line-height:1.0;letter-spacing:-2px;'
        f'color:{ink};margin-top:30px;">{br(title)}</div>'
    )
    if sub:
        parts.append(
            f'<div style="font-size:31px;line-height:1.4;color:{sub_col};'
            f'margin-top:26px;max-width:640px;">{br(sub)}</div>'
        )
    return (f'<div style="position:absolute;left:{MARGIN}px;top:118px;'
            f'right:{MARGIN}px;">{"".join(parts)}</div>')


def footer_html(page: int, total: int, project: str, footnote: str) -> str:
    left = project if not footnote else f"{project} · {footnote}"
    return (
        f'<div style="position:absolute;left:{MARGIN}px;bottom:40px;font-size:22px;'
        f'color:{FOOT};">{esc(left)}</div>'
        f'<div style="position:absolute;right:{MARGIN}px;bottom:40px;font-size:22px;'
        f'color:{FOOT};">{page:02d} / {total:02d}</div>'
    )


# ---------------------------------------------------------------------------
# Visuals -> HTML fragment (absolutely positioned within the page)
# ---------------------------------------------------------------------------

ZONE = (MARGIN, 720, W - 2 * MARGIN, 560)


def v_image(spec, ctx):
    mode = spec.get("mode", "halfpage")
    path = spec["path"]
    cap = spec.get("caption")
    uri = image_data_uri(path)
    if mode == "fullbleed":
        ctx["page_bg_image"] = uri
        return (
            f'<div style="position:absolute;left:0;top:0;width:{W}px;height:540px;'
            f'background:linear-gradient(180deg,{BG} 0%,rgba(20,53,33,0.80) 40%,rgba(20,53,33,0) 100%);"></div>'
            f'<div style="position:absolute;left:0;bottom:0;width:{W}px;height:220px;'
            f'background:linear-gradient(0deg,{BG} 0%,rgba(20,53,33,0) 100%);"></div>'
        )
    if mode == "contained":
        x, y, w, h = MARGIN + 80, 760, W - 2 * (MARGIN + 80), 470
    else:  # halfpage (default)
        x, y, w, h = MARGIN, 706, W - 2 * MARGIN, 576
    cap_html = ""
    if cap:
        cap_html = (
            f'<div style="position:absolute;left:24px;top:20px;font-size:20px;'
            f'font-weight:700;letter-spacing:3px;color:{WHITE};text-transform:uppercase;'
            f'background:rgba(16,40,26,0.55);padding:8px 16px;border-radius:10px;">{esc(cap)}</div>'
        )
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'border-radius:30px;overflow:hidden;background:{BG_PANEL};">'
        f'<div style="width:100%;height:100%;background-image:url(\'{uri}\');'
        f'background-size:cover;background-position:center;"></div>{cap_html}</div>'
    )


def v_icon(spec, ctx):
    name = spec["name"]
    pos = spec.get("pos", "right")
    frame = spec.get("frame", False)
    size = spec.get("size", 300)
    svg = icon_svg(name, size, stroke=WHITE, accent=LIME, width=spec.get("stroke", 6.0))
    box = size
    if frame:
        pad = 56
        svg = (
            f'<div style="width:{size + 2*pad}px;height:{size + 2*pad}px;'
            f'border:6px solid {WHITE};border-radius:36px;display:table-cell;'
            f'vertical-align:middle;text-align:center;">{svg}</div>'
        )
        box = size + 2 * pad
    if pos == "right":
        return f'<div style="position:absolute;right:{MARGIN}px;top:300px;">{svg}</div>'
    x, y, w, h = ZONE
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'text-align:center;"><div style="display:inline-block;margin-top:{(h-box)//2}px;">{svg}</div></div>')


def v_checklist(spec, ctx):
    x, y, w, h = MARGIN, 700, W - 2 * MARGIN, 582
    items = spec["items"]
    done = sum(1 for it in items if it.get("done"))
    header = spec.get("header", "")
    sub = spec.get("sub")
    max_items = spec.get("max_items", 7)
    shown = items[:max_items]
    extra = len(items) - len(shown)
    rows = []
    for i, it in enumerate(shown):
        is_done = it.get("done", False)
        box = (
            f'<div style="width:34px;height:34px;border-radius:9px;background:{LIME};'
            f'display:table-cell;vertical-align:middle;text-align:center;">'
            f'<span style="color:{INK};font-size:22px;font-weight:900;">&#10003;</span></div>'
            if is_done else
            f'<div style="width:34px;height:34px;border-radius:9px;border:3px solid #c9c2b0;"></div>'
        )
        txt_style = (f'color:{INK_MUTE};text-decoration:line-through;'
                     if is_done else f'color:{INK};')
        sep = "" if i == 0 else f'border-top:2px solid {CREAM_LINE};'
        rows.append(
            f'<tr><td style="padding:20px 0;{sep}width:54px;vertical-align:middle;">{box}</td>'
            f'<td style="padding:20px 0 20px 18px;{sep}font-size:28px;vertical-align:middle;{txt_style}">{esc(it["text"])}</td></tr>'
        )
    if extra > 0:
        rows.append(
            f'<tr><td colspan="2" style="padding:18px 0 0;font-size:24px;color:{INK_MUTE};">'
            f'+ {extra} til</td></tr>'
        )
    count = (f'<span style="font-size:24px;font-weight:400;color:{INK_MUTE};margin-left:14px;">'
             f'{done}/{len(items)}</span>')
    sub_html = (f'<div style="font-size:24px;color:{INK_MUTE};margin-top:8px;">{esc(sub)}</div>'
                if sub else "")
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'background:{CREAM};border-radius:30px;box-sizing:border-box;padding:42px 46px;">'
        f'<div style="font-size:30px;font-weight:900;color:{INK};">{esc(header)}{count}</div>'
        f'{sub_html}'
        f'<table style="width:100%;border-collapse:collapse;margin-top:14px;">{"".join(rows)}</table>'
        f'</div>'
    )


def v_step_cards(spec, ctx):
    cards = spec["cards"]
    n = len(cards)
    arrows = spec.get("arrows", True)
    x0, y0, w, h = MARGIN, 840, W - 2 * MARGIN, 360
    gap = 34
    cw = (w - gap * (n - 1)) / n
    frags = []
    for i, c in enumerate(cards):
        cx = x0 + i * (cw + gap)
        label = (f'<div style="font-size:20px;font-weight:700;letter-spacing:3px;'
                 f'color:{SUB};text-transform:uppercase;">{esc(c.get("label",""))}</div>'
                 if c.get("label") else "")
        title = (f'<div style="font-family:\'Lato\',Arial,sans-serif;font-weight:900;'
                 f'font-size:88px;color:{LIME};line-height:1;margin-top:6px;">{esc(c.get("title",""))}</div>'
                 if c.get("title") else "")
        sub = (f'<div style="font-size:25px;color:{WHITE};margin-top:14px;">{esc(c.get("sub",""))}</div>'
               if c.get("sub") else "")
        frags.append(
            f'<div style="position:absolute;left:{cx:.1f}px;top:{y0}px;width:{cw:.1f}px;height:{h}px;'
            f'background:{BG_PANEL};border:2px solid {PANEL_LINE};border-radius:26px;'
            f'box-sizing:border-box;padding:34px 30px;">{label}{title}{sub}</div>'
        )
        if arrows and i < n - 1:
            ax = cx + cw + gap / 2
            frags.append(
                f'<div style="position:absolute;left:{ax-16:.1f}px;top:{y0 + h//2 - 28}px;'
                f'font-size:48px;color:{LIME};">&rarr;</div>'
            )
    return "".join(frags)


def v_stat_cards(spec, ctx):
    cards = spec["cards"][:4]
    n = len(cards)
    x0, y0, w, h = MARGIN, 720, W - 2 * MARGIN, 560
    gap = 30
    if n <= 2:
        cw = (w - gap * (n - 1)) / n
        cells = [(x0 + i * (cw + gap), y0, cw, h) for i in range(n)]
    else:
        cw = (w - gap) / 2
        ch = (h - gap) / 2
        cells = []
        for i in range(n):
            r, c = divmod(i, 2)
            cells.append((x0 + c * (cw + gap), y0 + r * (ch + gap), cw, ch))
    frags = []
    for (cx, cy, cw_, ch_), c in zip(cells, cards):
        col = STAT_COLORS.get(c.get("color", "lime"), LIME)
        big = (f'<div style="font-family:\'Lato\',Arial,sans-serif;font-weight:900;'
               f'font-size:96px;color:{col};line-height:1;">{esc(c.get("big",""))}</div>')
        l1 = (f'<div style="font-size:24px;color:{SUB};margin-top:18px;">{esc(c.get("line1",""))}</div>'
              if c.get("line1") else "")
        l2 = (f'<div style="font-size:27px;font-weight:700;color:{WHITE};margin-top:4px;">{esc(c.get("line2",""))}</div>'
              if c.get("line2") else "")
        frags.append(
            f'<div style="position:absolute;left:{cx:.1f}px;top:{cy:.1f}px;width:{cw_:.1f}px;'
            f'height:{ch_:.1f}px;background:{BG_PANEL};border:2px solid {PANEL_LINE};'
            f'border-radius:26px;box-sizing:border-box;padding:34px;">{big}{l1}{l2}</div>'
        )
    return "".join(frags)


def v_url_cta(spec, ctx):
    x, y, w, h = MARGIN, 760, W - 2 * MARGIN, 470
    label = (f'<div style="font-size:22px;font-weight:700;letter-spacing:4px;color:{LIME};'
             f'text-transform:uppercase;">{esc(spec["label"])}</div>'
             if spec.get("label") else "")
    url = (f'<div style="font-family:\'Lato\',Arial,sans-serif;font-weight:900;font-size:50px;'
           f'color:{WHITE};margin-top:18px;word-break:break-all;">{esc(spec["url"])}</div>'
           if spec.get("url") else "")
    lines = ""
    for ln in spec.get("lines", []):
        lines += f'<div style="font-size:28px;color:{SUB};margin-top:10px;">{esc(ln)}</div>'
    cta = (f'<div style="font-size:30px;font-weight:700;color:{LIME};margin-top:30px;">{esc(spec["cta"])}</div>'
           if spec.get("cta") else "")
    return (
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'background:{BG_PANEL};border:2px solid {PANEL_LINE};border-radius:30px;'
        f'box-sizing:border-box;padding:48px 50px;">{label}{url}{lines}{cta}</div>'
    )


def v_sankey(spec, ctx):
    """Multi-stage Sankey, ported to SVG, on a light cream card."""
    data = json.loads(Path(spec["data_path"]).read_text())
    years = spec.get("years", data.get("elections"))
    threshold = spec.get("threshold", 0.5)
    caption = spec.get("caption")
    party_info = {p["code"]: p for p in data["parties"]}
    shares = data["electorateShares"]
    order = [p["code"] for p in data["parties"]]
    transitions = {(t["from"], t["to"]): t["matrix"] for t in data["transitions"]}

    cx, cy, cw, ch = MARGIN, 706, W - 2 * MARGIN, 576
    pad = 44
    cap_h = 72 if caption else 0
    ix, iy = cx + pad, cy + pad + cap_h
    iw, ih = cw - 2 * pad, ch - 2 * pad - cap_h
    n_cols = len(years)
    col_x = [ix + iw * (i + 0.5) / n_cols for i in range(n_cols)]
    bar_w = iw * 0.045
    gap = ih * 0.012
    totals = {y: sum(shares[y][p] for p in order) for y in years}

    pos = {}
    for yr in years:
        scale = (ih - gap * (len(order) - 1)) / totals[yr]
        cur = iy
        for p in order:
            hgt = shares[yr][p] * scale
            pos[(yr, p)] = (cur, cur + hgt)
            cur += hgt + gap

    paths = []
    for ci in range(n_cols - 1):
        sy, dy = years[ci], years[ci + 1]
        if (sy, dy) not in transitions:
            continue
        mat = transitions[(sy, dy)]
        x_src = col_x[ci] + bar_w / 2
        x_dst = col_x[ci + 1] - bar_w / 2
        ss = (ih - gap * (len(order) - 1)) / totals[sy]
        ds = (ih - gap * (len(order) - 1)) / totals[dy]
        so = {p: 0.0 for p in order}
        do = {p: 0.0 for p in order}
        flows = []
        for s in order:
            for d in order:
                f = shares[dy][d] * mat[s][d] / 100.0
                if f >= threshold:
                    flows.append((s, d, f))
        flows.sort(key=lambda t: -t[2])
        for s, d, f in flows:
            s_top = pos[(sy, s)][0]
            d_top = pos[(dy, d)][0]
            sh, dh = f * ss, f * ds
            yst = s_top + so[s]; ysb = yst + sh
            ydt = d_top + do[d]; ydb = ydt + dh
            so[s] += sh; do[d] += dh
            xm = (x_src + x_dst) / 2
            col = party_info[s]["color"]
            paths.append(
                f'<path d="M{x_src:.1f},{yst:.1f} C{xm:.1f},{yst:.1f} {xm:.1f},{ydt:.1f} {x_dst:.1f},{ydt:.1f} '
                f'L{x_dst:.1f},{ydb:.1f} C{xm:.1f},{ydb:.1f} {xm:.1f},{ysb:.1f} {x_src:.1f},{ysb:.1f} Z" '
                f'fill="{col}" fill-opacity="0.4"/>'
            )
    bars, labels = [], []
    for ci, yr in enumerate(years):
        bx = col_x[ci] - bar_w / 2
        for p in order:
            yt, yb = pos[(yr, p)]
            bars.append(f'<rect x="{bx:.1f}" y="{yt:.1f}" width="{bar_w:.1f}" height="{yb-yt:.1f}" '
                        f'fill="{party_info[p]["color"]}"/>')
        labels.append(f'<text x="{col_x[ci]:.1f}" y="{iy-16:.1f}" text-anchor="middle" '
                      f'font-size="26" font-weight="700" fill="{INK_BODY}">{esc(yr)}</text>')
    last = years[-1]
    for p in order:
        if p == "IS":
            continue
        yt, yb = pos[(last, p)]
        if yb - yt < 16:
            continue
        labels.append(f'<text x="{col_x[-1]+bar_w/2+10:.1f}" y="{(yt+yb)/2+8:.1f}" '
                      f'font-size="20" font-weight="600" fill="{INK}">{esc(p)}</text>')
    cap_html = (f'<text x="{cx+pad:.1f}" y="{cy+pad+18:.1f}" font-size="22" font-weight="700" '
                f'letter-spacing="2" fill="{INK_MUTE}">{esc(caption.upper())}</text>' if caption else "")
    svg = (f'<svg width="{cw}" height="{ch}" viewBox="{cx} {cy} {cw} {ch}" '
           f'xmlns="http://www.w3.org/2000/svg">{cap_html}{"".join(paths)}{"".join(bars)}{"".join(labels)}</svg>')
    return (f'<div style="position:absolute;left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px;'
            f'background:{CREAM};border-radius:30px;overflow:hidden;">{svg}</div>')


RENDERERS = {
    "image": v_image, "icon": v_icon, "checklist": v_checklist,
    "step_cards": v_step_cards, "stat_cards": v_stat_cards,
    "url_cta": v_url_cta, "sankey": v_sankey,
}


# ---------------------------------------------------------------------------
# Page + build
# ---------------------------------------------------------------------------

def slide_html(slide, page, total, project, footnote, fonts_dir, base_dir):
    ctx = {"page_bg_image": None}
    visual = slide.get("visual") or {"type": "none"}
    vtype = visual.get("type", "none")
    spec = dict(visual)
    for k in ("path", "data_path"):
        if k in spec and not Path(spec[k]).is_absolute():
            spec[k] = str((base_dir / spec[k]).resolve())
    vis_html = ""
    if vtype != "none":
        renderer = RENDERERS.get(vtype)
        if renderer is None:
            raise ValueError(f"unknown visual type: {vtype}")
        vis_html = renderer(spec, ctx)

    bg_layer = ""
    if ctx["page_bg_image"]:
        bg_layer = (f'<div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;'
                    f'background-image:url(\'{ctx["page_bg_image"]}\');'
                    f'background-size:cover;background-position:center;"></div>')

    head = heading_html(slide.get("kicker", ""), slide.get("title", ""),
                        slide.get("sub"), slide.get("title_size", 118), True)
    ff = font_face_css(fonts_dir)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{ff}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:{W}px;height:{H}px;}}
body{{font-family:'Lato','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased;}}
.page{{position:relative;width:{W}px;height:{H}px;background:{BG};overflow:hidden;}}
</style></head><body><div class="page">
{bg_layer}{progress_html(page, total)}{head}{vis_html}
{footer_html(page, total, project, footnote)}
</div></body></html>"""


def render_pdf(html_str, out_pdf, tmp):
    html_file = tmp / "slide.html"
    html_file.write_text(html_str, encoding="utf-8")
    # wkhtmltopdf quirk: when --page-width equals the content's CSS width it
    # honours width but under-scales height. Expressing the page at the
    # pt-equivalent (0.75x the px design) forces uniform fit-to-width scaling,
    # so the 1080x1350 content fills the page 100% at a true 4:5 aspect.
    pw = round(W * 0.75)
    ph = round(H * 0.75)
    cmd = [
        "wkhtmltopdf", "--enable-local-file-access", "--disable-smart-shrinking",
        "--dpi", "96", "--page-width", f"{pw}px", "--page-height", f"{ph}px",
        "--margin-top", "0", "--margin-bottom", "0",
        "--margin-left", "0", "--margin-right", "0",
        "--encoding", "utf-8", str(html_file), str(out_pdf),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 and not out_pdf.exists():
        raise RuntimeError(f"wkhtmltopdf failed:\n{res.stderr}")


def build(config, out_path, config_dir):
    slides = config["slides"]
    total = len(slides)
    project = config.get("project", "")
    footnote = config.get("footnote", "")
    fonts_dir = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    if not font_face_css(fonts_dir).strip():
        print(f"NB: bundled Lato not found in {fonts_dir} — falling back to the "
              f"system sans stack (headlines will not look final).", file=sys.stderr)
    writer = PdfWriter()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, slide in enumerate(slides, 1):
            page_pdf = tmp / f"slide_{i:02d}.pdf"
            render_pdf(
                slide_html(slide, i, total, project, footnote, fonts_dir, config_dir),
                page_pdf, tmp,
            )
            # Take only the first page: a 1px layout overflow can make
            # wkhtmltopdf emit a trailing near-empty page per slide.
            writer.add_page(PdfReader(str(page_pdf)).pages[0])
        with open(out_path, "wb") as fh:
            writer.write(fh)
    return out_path


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    config = json.loads(args.config.read_text())
    if args.out:
        out_path = args.out
    elif config.get("out"):
        oc = Path(config["out"])
        out_path = oc if oc.is_absolute() else args.config.parent / oc
    else:
        out_path = args.config.with_suffix(".pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    build(config, out_path, args.config.parent.resolve())
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
