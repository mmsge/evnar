---
title: favicon
---

# `favicon`

> Set opp favicon-ar korrekt for kva som helst nettprosjekt — lag frå grunnen av eller fiks eit øydelagt oppsett.

## Kva han gjer

Lagar ein komplett, produksjonsklar favicon-implementasjon (frå SVG, emoji eller
tekst) eller reparerer eit eksisterande, brote oppsett. Genererer alle formata
som trengst — `favicon.svg`, `favicon.ico`, `apple-touch-icon.png`, `icon-192.png`,
`icon-512.png` — pluss web-manifest og `<head>`-markup. Unngår inline
`data:`-URI-ar (som Google og sosiale medium ikkje klarar å hente).

## Når han slår til

_«add a favicon», «fix my favicon», «favicon not showing», «site icon»,
«tab icon», «emoji favicon», «PWA icons», «web manifest icons»_ — eller når ein
favicon ikkje dukkar opp i Google-søk, lenkeførehandsvisningar eller faner.

## Kva som følgjer med

- `references/` — rammeverk-spesifikke guidar: `plain-html`, `nextjs-app`,
  `nextjs-pages`, `nuxt`, `sveltekit`, `astro`, `vite`

## Føresetnader

Ingen spesielle (eit verktøy for å rastrere SVG til PNG/ICO er greitt å ha).

## Bruk

- **APM-ruta:** etter `apm install` ligg `favicon` i agenten din.
- **Manuelt:** kopier `.apm/skills/favicon/` (med `references/`) til skills-mappa.
  Sjå [Last ned og last inn](../installering/manuell.md).
