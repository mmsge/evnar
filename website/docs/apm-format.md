---
title: APM-kjeldeformatet
sidebar_label: APM-kjeldeformatet
sidebar_position: 4
---

# APM-kjeldeformatet

`evnar` er ei **APM-pakke**. Rot-fila `apm.yml` deklarerer pakke-metadata,
mål-klientar, avhengnader, MCP-serverar og scripts. Mappa `.apm/` er
kjeldetreet du redigerer.

## Kjeldetreet

```text
.apm/
├── skills/                 # alle skills — éi mappe per skill
│   └── <namn>/
│       ├── SKILL.md         # påkravd: frontmatter (name + description) + instruksjon
│       ├── references/      # valfri djup kontekst
│       ├── scripts/         # valfrie hjelpescript
│       └── assets/          # valfrie malar/data/fontar
├── instructions/           # alltid-på-reglar for klientane
├── prompts/                # *.prompt.md — attbrukande prompts
├── agents/                 # *.agent.md — namngjevne agentar
├── hooks/                  # livssyklus-hooks
└── context/               # delte kontekst-fragment
```

## Dagleg bruk

Installer APM og køyr:

```bash
apm install --target all,agent-skills
```

…eller bruk wrapperen `./install.sh`. Wrapperen kallar same kommando når `apm`
ligg på `PATH`, og avsluttar med ein feil dersom APM ikkje er installert. Sjå
[APM-ruta](./installering/apm.md) for detaljar.

## Legge til lokalt innhald

| Type | Slik gjer du |
|---|---|
| Skill | Legg til ei mappe under `.apm/skills/<namn>/` med ei `SKILL.md` |
| Instruksjon | Legg til Markdown-filer under `.apm/instructions/` |
| Prompt | Legg til filer som heiter `*.prompt.md` under `.apm/prompts/` |
| Agent | Legg til filer som heiter `*.agent.md` under `.apm/agents/` |
| MCP-server | Legg til oppføringar under `dependencies.mcp` i `apm.yml` |

Generert utdata blir ignorert av git. Rediger `.apm/` og køyr `apm install` på
nytt.

## Nyttige kommandoar

```bash
apm targets
apm install --target all,agent-skills --dry-run
apm install --target all,agent-skills
apm audit
apm pack
```
