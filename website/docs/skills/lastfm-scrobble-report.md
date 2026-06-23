---
title: lastfm-scrobble-report
---

# `lastfm-scrobble-report`

> Lag ein fyldig Last.fm-scrobble-rapport (PDF + CSV) for kva artist som helst i lyttehistorikken.

## Kva han gjer

Lagar ein fargekoda PDF over fleire sider med per-album-tabellar og diagram,
pluss ein tilhøyrande CSV. Skillen hentar album- og spor-data frå Last.fm (via
MCP), handterer randtilfelle (deluxe-utgåver, singlar, teiknkoding) og køyrer eit
Python-script for sjølve rapporten. Standard-brukar er `mvrkws`.

## Når han slår til

_«analyser scrobblane mine for [artist]», «kor mange gonger har eg spelt …»,
«scrobble report», «listening report», «Last.fm breakdown»_ — sjølv om du ikkje
seier «PDF» eller «CSV».

## Kva som følgjer med

- `references/workflow.md` — heile data-innsamlinga
- `references/known_issues.md` — API-fallgruver (teiknkoding o.l.)
- `references/data_schema.md` — Python-dict-skjemaet
- `scripts/generate_report.py` — PDF/CSV-generatoren

## Føresetnader

Python med `reportlab`, `matplotlib` og `pillow`; tilgang til Last.fm-data
(MCP).

## Bruk

- **APM-ruta:** etter `apm install` ligg `lastfm-scrobble-report` i agenten din.
- **Manuelt:** kopier `.apm/skills/lastfm-scrobble-report/` (med `references/` og
  `scripts/`) til skills-mappa. Sjå [Last ned og last inn](../installering/manuell.md).
