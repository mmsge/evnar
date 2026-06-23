---
title: new-project-scaffold
---

# `new-project-scaffold`

> Set opp nye programvareprosjekt i tomme repo med komplett, produksjonsklar struktur.

## Kva han gjer

Bootstrap-ar eit heilt prosjekt-skjelett i eitt jafs: ein Docusaurus-venleg
`/docs`-mappe, ein rot-README med badges og køyre-instruksjonar, full
test-dekning (mål ≥ 80 % linjedekning), GitHub Actions for lint/format/test/
coverage, og språk-spesifikke referansefiler. Skillen samlar først krava
(namn, språk, rammeverk, type) og vel deretter rett mal.

## Når han slår til

_«start a new project», «scaffold a repo», «bootstrap a project», «set up a new
app», «initialise a project», «blank repo», «new codebase»_. Skillen improviserer
aldri ein prosjektstruktur utan å bruke malane.

## Kva som følgjer med

- `references/` — scaffold-malar for `typescript`, `python`, `go`, `rust`,
  `react` og ein `generic` fallback

## Føresetnader

Ingen spesielle utover køyretida til språket du vel.

## Bruk

- **APM-ruta:** etter `apm install` ligg `new-project-scaffold` i agenten din.
- **Manuelt:** kopier `.apm/skills/new-project-scaffold/` (med `references/`) til
  skills-mappa. Sjå [Last ned og last inn](../installering/manuell.md).
