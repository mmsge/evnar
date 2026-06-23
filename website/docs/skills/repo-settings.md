---
title: repo-settings
---

# `repo-settings`

> Set standard GitHub-innstillingar på eit repo frå ein medfølgjande `settings.json`.

## Kva han gjer

Bruker eit fast sett med repo-innstillingar via eit idempotent PATCH mot
GitHub-API-et: squash-only-merging, auto-sletting av head-branchar, tillat
auto-merge, foreslå PR-branch-oppdatering, issues/projects på, wiki/discussions
av. Skill-mappa er sjølvstendig og kan kopierast rett til `~/.claude/skills/`.

## Når han slår til

Når du lagar eller set opp eit nytt repo, når du blir bedd om å standardisere
eller fikse repo-innstillingar, eller rett etter `gh repo create`.

## Kva som følgjer med

- `apply.sh` — script som gjer PATCH-kallet
- `settings.json` — det kanoniske innstillings-settet

## Føresetnader

`gh` CLI (autentisert) og `jq`.

## Bruk

- **APM-ruta:** etter `apm install` ligg `repo-settings` i agenten din.
- **Manuelt:** kopier `.apm/skills/repo-settings/` (med `apply.sh` og
  `settings.json`) til skills-mappa. Sjå [Last ned og last inn](../installering/manuell.md).
