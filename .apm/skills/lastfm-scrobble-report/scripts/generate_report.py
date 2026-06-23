"""
lastfm-scrobble-report: generate_report.py
===========================================
Generates a PDF report and CSV for any artist's Last.fm scrobble data.

Usage (from within Claude's Python environment):
    from scripts.generate_report import generate_report
    generate_report(report_data, output_dir="/mnt/user-data/outputs")

Or run directly:
    python scripts/generate_report.py  # uses DEMO_DATA below

Input: report_data dict — see references/data_schema.md for full schema.
Output: <artist_slug>_scrobbles.pdf and <artist_slug>_scrobbles.csv
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import os
import csv
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

# ── Default colour palette (auto-assigned per album if no color key given) ────
PALETTE = [
    "#6c5ce7",  # purple
    "#00b894",  # green
    "#e17055",  # coral
    "#0984e3",  # blue
    "#fd79a8",  # pink
    "#a29bfe",  # lavender
]
COLOR_DELUXE   = "#fdcb6e"   # gold   — deluxe bonus tracks
COLOR_SINGLE   = "#74b9ff"   # light blue — standalone singles
COLOR_UNRES    = "#b2bec3"   # grey   — unresolvable
COLOR_DARK     = "#2d3436"
COLOR_MID      = "#636e72"
COLOR_LIGHT    = "#dfe6e9"
COLOR_RED      = "#d63031"


# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')


def fig_to_rl_image(fig, width_cm=16):
    """Convert a matplotlib figure to a ReportLab Image flowable."""
    from PIL import Image as PILImage
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    pil = PILImage.open(io.BytesIO(buf.getvalue()))
    aspect = pil.height / pil.width
    buf.seek(0)
    w = width_cm * cm
    return Image(buf, width=w, height=w * aspect)


def _bar_style(ax, title, xlabel=None, ylabel=None):
    ax.set_facecolor('#fafafa')
    ax.set_title(title, fontsize=11, fontweight='bold', color=COLOR_DARK, pad=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9, color=COLOR_MID)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9, color=COLOR_MID)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_LIGHT)
    ax.spines['bottom'].set_color(COLOR_LIGHT)
    ax.tick_params(colors=COLOR_MID)


def track_bar_color(track, album_color):
    note = track.get("note", "")
    if track.get("plays") is None:
        return COLOR_UNRES
    if note == "Deluxe bonus":
        return COLOR_DELUXE
    if note == "Single (not on album)":
        return COLOR_SINGLE
    return album_color


# ── Charts ────────────────────────────────────────────────────────────────────

def chart_album_totals(albums_with_colors):
    """Horizontal bar chart of totals per album."""
    labels = [a["title"] for a in albums_with_colors]
    # Use individual track sums when album_total is 0
    values = []
    for a in albums_with_colors:
        if a["album_total"] > 0:
            values.append(a["album_total"])
        else:
            values.append(sum(t["plays"] or 0 for t in a["tracks"]))
    clrs = [a["_color"] for a in albums_with_colors]

    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 0.9 + 1)))
    fig.patch.set_facecolor('#fafafa')
    _bar_style(ax, "Scrobbles by Album", xlabel="Scrobbles")

    y_pos = range(len(labels))
    bars = ax.barh(list(y_pos), values, color=clrs, height=0.55, zorder=3)
    ax.set_yticks(list(y_pos))
    short_labels = [l[:30] + "…" if len(l) > 31 else l for l in labels]
    ax.set_yticklabels(short_labels, fontsize=9)
    ax.invert_yaxis()
    ax.xaxis.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax.set_axisbelow(True)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{val:,}', va='center', fontsize=9,
                fontweight='bold', color=COLOR_DARK)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=14)


def chart_pie(albums_with_colors):
    """Pie chart of scrobble share."""
    sizes, labels, clrs = [], [], []
    for a in albums_with_colors:
        v = a["album_total"] if a["album_total"] > 0 else sum(t["plays"] or 0 for t in a["tracks"])
        if v > 0:
            sizes.append(v)
            labels.append(a["title"])
            clrs.append(a["_color"])

    fig, ax = plt.subplots(figsize=(5.5, 4))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=clrs,
        autopct='%1.1f%%', startangle=140,
        textprops={'fontsize': 8, 'color': COLOR_DARK},
        pctdistance=0.78,
    )
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_color('white')
        at.set_fontweight('bold')

    ax.set_title("Scrobble Share", fontsize=11, fontweight='bold',
                 color=COLOR_DARK, pad=10)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=10)


def chart_tracks(album):
    """Horizontal bar chart for tracks within one album."""
    tracks = album["tracks"]
    names  = [t["title"] for t in tracks]
    values = [t["plays"] or 0 for t in tracks]
    clrs   = [track_bar_color(t, album["_color"]) for t in tracks]
    short  = [n[:28] + "…" if len(n) > 29 else n for n in names]

    fig, ax = plt.subplots(figsize=(8, max(4, len(tracks) * 0.42 + 1.5)))
    fig.patch.set_facecolor('#fafafa')
    _bar_style(ax, f'{album["title"]} — Track Scrobbles', xlabel="Scrobbles")

    y_pos = range(len(short))
    bars = ax.barh(list(y_pos), values, color=clrs, height=0.6, zorder=3)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(short, fontsize=8)
    ax.invert_yaxis()
    ax.xaxis.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax.set_axisbelow(True)

    max_val = max(values) if values else 1
    for bar, val, t in zip(bars, values, tracks):
        label = "?" if t["plays"] is None else str(val)
        ax.text(bar.get_width() + max_val * 0.01,
                bar.get_y() + bar.get_height() / 2,
                label, va='center', fontsize=8,
                color=COLOR_MID if t["plays"] is None else COLOR_DARK)

    # Legend
    legend_items = [mpatches.Patch(color=album["_color"], label='Album track')]
    notes_seen = {t["note"] for t in tracks}
    if "Deluxe bonus" in notes_seen:
        legend_items.append(mpatches.Patch(color=COLOR_DELUXE, label='Deluxe bonus'))
    if "Single (not on album)" in notes_seen:
        legend_items.append(mpatches.Patch(color=COLOR_SINGLE, label='Single (not on album)'))
    if any(t["plays"] is None for t in tracks):
        legend_items.append(mpatches.Patch(color=COLOR_UNRES, label='Unresolvable (API issue)'))
    if len(legend_items) > 1:
        ax.legend(handles=legend_items, fontsize=7.5, loc='lower right',
                  framealpha=0.7, edgecolor=COLOR_LIGHT)

    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=14)


# ── Table builders ─────────────────────────────────────────────────────────────

def build_track_table(album):
    rows = [['#', 'Track', 'Plays', 'Note']]
    for t in album["tracks"]:
        plays = '⚠ n/a' if t["plays"] is None else str(t["plays"])
        rows.append([str(t["number"]), t["title"], plays, t.get("note", "")])
    total = album["album_total"] if album["album_total"] > 0 else sum(t["plays"] or 0 for t in album["tracks"])
    rows.append(['', 'TOTAL (Last.fm album-tagged)', str(total) if album["album_total"] > 0 else f'~{total} (track sum)', ''])
    return rows


def track_table_style(color_hex):
    hdr = HexColor(color_hex)
    return TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), hdr),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 8),
        ('FONTSIZE',     (0, 1), (-1, -1), 7.5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -2), [colors.white, HexColor('#f5f6fa')]),
        ('BACKGROUND',   (0, -1), (-1, -1), HexColor('#ecf0f1')),
        ('FONTNAME',     (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN',        (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN',        (0, 0), (0, -1), 'CENTER'),
        ('GRID',         (0, 0), (-1, -1), 0.3, HexColor(COLOR_LIGHT)),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
    ])


# ── CSV export ────────────────────────────────────────────────────────────────

def write_csv(report_data, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Album', 'Year', 'Track #', 'Track', 'Your Scrobbles', 'Note'])
        for album in report_data["albums"]:
            for t in album["tracks"]:
                plays = '⚠ unresolvable' if t["plays"] is None else str(t["plays"])
                writer.writerow([
                    album["title"],
                    album.get("year", ""),
                    t["number"],
                    t["title"],
                    plays,
                    t.get("note", ""),
                ])
            total = album["album_total"] if album["album_total"] > 0 else ""
            writer.writerow([album["title"], album.get("year", ""),
                             '', 'ALBUM TOTAL (Last.fm tagged)', total, ''])
            writer.writerow([])  # blank separator


# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf(report_data, path):
    albums = report_data["albums"]

    # Auto-assign colours
    for i, album in enumerate(albums):
        if "_color" not in album:
            album["_color"] = album.get("color", PALETTE[i % len(PALETTE)])

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()

    title_sty = ParagraphStyle('T', fontSize=26, fontName='Helvetica-Bold',
                               textColor=HexColor(COLOR_DARK), alignment=TA_CENTER, spaceAfter=4)
    sub_sty   = ParagraphStyle('S', fontSize=11, fontName='Helvetica',
                               textColor=HexColor(COLOR_MID), alignment=TA_CENTER, spaceAfter=2)
    sec_sty   = ParagraphStyle('H', fontSize=14, fontName='Helvetica-Bold',
                               textColor=HexColor(COLOR_DARK), spaceBefore=14, spaceAfter=6)
    body_sty  = ParagraphStyle('B', fontSize=9, fontName='Helvetica',
                               textColor=HexColor(COLOR_MID), spaceAfter=6, leading=14)
    cap_sty   = ParagraphStyle('C', fontSize=8, fontName='Helvetica-Oblique',
                               textColor=HexColor(COLOR_MID), alignment=TA_CENTER, spaceAfter=8)

    story = []

    # ── Cover / overview ──────────────────────────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph(report_data["artist"], title_sty))
    story.append(Paragraph("Last.fm Scrobble Report", sub_sty))
    story.append(Paragraph(
        f'Last.fm user: {report_data["username"]}  ·  Generated: {report_data.get("date", "")}',
        sub_sty))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1.5,
                            color=HexColor(COLOR_RED), spaceAfter=14))

    # Summary table
    grand_total = sum(
        a["album_total"] if a["album_total"] > 0 else sum(t["plays"] or 0 for t in a["tracks"])
        for a in albums
    )
    summary_rows = [['Album', 'Year', 'Tracks', 'Your Scrobbles']]
    for a in albums:
        total = a["album_total"] if a["album_total"] > 0 else sum(t["plays"] or 0 for t in a["tracks"])
        summary_rows.append([a["title"], str(a.get("year", "")),
                             str(len(a["tracks"])), f'{total:,}'])
    summary_rows.append(['GRAND TOTAL', '', '', f'{grand_total:,}'])

    summary_table = Table(summary_rows, colWidths=[8.5*cm, 2*cm, 2.5*cm, 4.5*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), HexColor(COLOR_RED)),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS',(0, 1), (-1, -2), [colors.white, HexColor('#f5f6fa')]),
        ('BACKGROUND',   (0, -1), (-1, -1), HexColor(COLOR_DARK)),
        ('TEXTCOLOR',    (0, -1), (-1, -1), colors.white),
        ('FONTNAME',     (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN',        (1, 0), (-1, -1), 'CENTER'),
        ('GRID',         (0, 0), (-1, -1), 0.3, HexColor(COLOR_LIGHT)),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.4*cm))

    # Overview charts
    story.append(Paragraph("Overview", sec_sty))
    bar_img = chart_album_totals(albums)
    pie_img = chart_pie(albums)
    row = Table([[bar_img, pie_img]], colWidths=[11*cm, 7*cm])
    row.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(row)

    # ── Per-album pages ───────────────────────────────────────────────────
    for album in albums:
        story.append(PageBreak())
        title_str = f'{album["title"]} ({album.get("year", "")})'
        story.append(Paragraph(title_str, sec_sty))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=HexColor(album["_color"]), spaceAfter=8))

        # Blurb
        total = album["album_total"] if album["album_total"] > 0 \
            else sum(t["plays"] or 0 for t in album["tracks"])
        n_unres = sum(1 for t in album["tracks"] if t["plays"] is None)
        n_deluxe = sum(1 for t in album["tracks"] if t.get("note") == "Deluxe bonus")
        blurb_parts = [f'{len(album["tracks"])} tracks listed.']
        if album["album_total"] > 0:
            blurb_parts.append(f'Last.fm album-tagged total: {album["album_total"]:,} plays.')
        if n_deluxe:
            blurb_parts.append(f'Includes {n_deluxe} deluxe bonus tracks.')
        if n_unres:
            blurb_parts.append(
                f'{n_unres} track(s) unresolvable individually due to curly-apostrophe '
                f'encoding — plays included in album total.')
        story.append(Paragraph(' '.join(blurb_parts), body_sty))

        # Track chart
        story.append(chart_tracks(album))
        story.append(Spacer(1, 0.3*cm))

        # Track table
        rows = build_track_table(album)
        tbl  = Table(rows, colWidths=[1*cm, 9*cm, 2.5*cm, 5*cm])
        tbl.setStyle(track_table_style(album["_color"]))
        story.append(tbl)

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor(COLOR_LIGHT)))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f'Data sourced via Last.fm API  ·  Generated {report_data.get("date", "")}  ·  '
        f'User: {report_data["username"]}',
        cap_sty))

    doc.build(story)


# ── Public entry point ────────────────────────────────────────────────────────

def generate_report(report_data, output_dir="/mnt/user-data/outputs"):
    """
    Generate PDF and CSV reports from report_data dict.
    Returns (pdf_path, csv_path).
    """
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(report_data["artist"])
    pdf_path = os.path.join(output_dir, f"{slug}_scrobbles.pdf")
    csv_path = os.path.join(output_dir, f"{slug}_scrobbles.csv")

    write_csv(report_data, csv_path)
    build_pdf(report_data, pdf_path)

    return pdf_path, csv_path


# ── Demo / smoke test ─────────────────────────────────────────────────────────

DEMO_DATA = {
    "artist":   "Maisie Peters",
    "username": "mvrkws",
    "date":     "25 March 2026",
    "albums": [
        {
            "title": "You Signed Up for This", "year": 2021, "album_total": 1509,
            "tracks": [
                {"number": 1,  "title": "You Signed Up for This",   "plays": 99,   "note": ""},
                {"number": 2,  "title": "I'm Trying (Not Friends)",  "plays": None, "note": "API encoding issue"},
                {"number": 3,  "title": "John Hughes Movie",         "plays": 102,  "note": "Pre-release single"},
                {"number": 4,  "title": "Outdoor Pool",              "plays": 101,  "note": ""},
                {"number": 5,  "title": "Love Him I Don't",          "plays": None, "note": "API encoding issue"},
                {"number": 6,  "title": "Psycho",                    "plays": 112,  "note": "Pre-release single"},
                {"number": 7,  "title": "Boy",                       "plays": 100,  "note": ""},
                {"number": 8,  "title": "Hollow",                    "plays": 104,  "note": ""},
                {"number": 9,  "title": "Villain",                   "plays": 99,   "note": ""},
                {"number": 10, "title": "Brooklyn",                  "plays": 102,  "note": "Pre-release single"},
                {"number": 11, "title": "Elvis Song",                "plays": 98,   "note": ""},
                {"number": 12, "title": "Talking to Strangers",      "plays": 138,  "note": ""},
                {"number": 13, "title": "Volcano",                   "plays": 110,  "note": ""},
                {"number": 14, "title": "Tough Act",                 "plays": 130,  "note": ""},
            ]
        },
        {
            "title": "The Good Witch", "year": 2023, "album_total": 2709,
            "tracks": [
                {"number": 1,   "title": "The Good Witch",                              "plays": 229,  "note": ""},
                {"number": 2,   "title": "Coming of Age",                               "plays": 212,  "note": ""},
                {"number": 3,   "title": "Watch",                                       "plays": 210,  "note": ""},
                {"number": 4,   "title": "Body Better",                                 "plays": 280,  "note": "Pre-release single"},
                {"number": 5,   "title": "Want You Back",                               "plays": 211,  "note": ""},
                {"number": 6,   "title": "The Band and I",                              "plays": 218,  "note": ""},
                {"number": 7,   "title": "You're Just a Boy (And I'm Kinda the Man)",   "plays": None, "note": "API encoding issue"},
                {"number": 8,   "title": "Lost the Breakup",                            "plays": 1440, "note": "Pre-release single"},
                {"number": 9,   "title": "Wendy",                                       "plays": 216,  "note": ""},
                {"number": 10,  "title": "Run",                                         "plays": 213,  "note": ""},
                {"number": 11,  "title": "Holy Revival",                                "plays": 259,  "note": "Deluxe bonus"},
                {"number": 12,  "title": "Yoko",                                        "plays": 108,  "note": "Deluxe bonus"},
                {"number": 13,  "title": "The Song",                                    "plays": 304,  "note": "Deluxe bonus"},
                {"number": 14,  "title": "Guy On A Horse",                              "plays": 105,  "note": "Deluxe bonus"},
                {"number": 15,  "title": "Truth Is",                                    "plays": 106,  "note": "Deluxe bonus"},
                {"number": 16,  "title": "The Last One",                                "plays": 108,  "note": "Deluxe bonus"},
                {"number": "—", "title": "Two Weeks Ago",                               "plays": 233,  "note": "Single (not on album)"},
            ]
        },
        {
            "title": "Florescence", "year": 2026, "album_total": 0,
            "tracks": [
                {"number": 2, "title": "Audrey Hepburn",            "plays": 312, "note": "Pre-release single"},
                {"number": 3, "title": "Say My Name In Your Sleep", "plays": 168, "note": "Pre-release single"},
                {"number": 8, "title": "My Regards",                "plays": 357, "note": "Pre-release single"},
                {"number": 9, "title": "You You You",               "plays": 301, "note": "Pre-release single"},
            ]
        },
    ]
}

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
    pdf, csv_f = generate_report(DEMO_DATA, output_dir=out)
    print(f"PDF: {pdf}")
    print(f"CSV: {csv_f}")
