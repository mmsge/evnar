---
title: git
---

# `git`

> Ekspert-assistent for git-arbeidsflyt: commits, branchar, PR-ar, kodegjennomgang og CI.

## Kva han gjer

Dekker alt frå lokale commits og branch-handtering til pull requests,
kodegjennomgang og CI-/Actions-sjekkar — på tvers av både **GitHub** og
**Forgejo**. Kjerneprinsippet er _«bruk det billegaste verktøyet som kan svare»_:
lokal `git` CLI først, så `gh`/`tea`, så MCP, så API. Han følgjer Conventional
Commits og passar på branch-tryggleik (aldri redigere standard-branchar direkte).

## Når han slår til

Når du arbeider i eit git-prosjekt — uavhengig av om du seier «git», «GitHub»,
«Forgejo», «PR», «branch», «commit», «push», «merge», «rebase» eller «CI». Òg
_«make a pull request», «check the build», «what branch am I on», «review this PR»_.

## Kva som følgjer med

- `references/github.md` — GitHub-spesifikk arbeidsflyt
- `references/forgejo.md` — Forgejo-spesifikk arbeidsflyt

## Føresetnader

`git`; valfritt `gh` (GitHub) eller `tea` (Forgejo) for rikare operasjonar.

## Bruk

- **APM-ruta:** etter `apm install` ligg `git` i agenten din.
- **Manuelt:** kopier `.apm/skills/git/` (med `references/`) til skills-mappa.
  Sjå [Last ned og last inn](../installering/manuell.md).
