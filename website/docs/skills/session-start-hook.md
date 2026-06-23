---
title: session-start-hook
---

# `session-start-hook`

> Lag SessionStart-hooks for Claude Code på nettet, så testar og lintarar verkar i web-økter.

## Kva han gjer

Analyserer manifesta til prosjektet (`package.json`, `pyproject.toml`,
`Cargo.toml`, `go.mod` osv.), lagar eit idempotent installasjonsscript som hentar
avhengnadene, validerer at lintar og testar køyrer, og registrerer hooken i
`.claude/settings.json`. Støttar async-modus (300 s timeout) og brukar
miljøvariablane `$CLAUDE_PROJECT_DIR`, `$CLAUDE_ENV_FILE` og `$CLAUDE_CODE_REMOTE`.

## Når han slår til

Når du vil setje opp eit repo for Claude Code på nettet, eller lage ein
SessionStart-hook som sikrar at prosjektet kan køyre testar og lintarar under
web-økter.

## Kva som følgjer med

- `SKILL.md` — analyse, script-design og registrering av hooken

## Føresetnader

Eit prosjekt med kjende manifest; Claude Code (web).

## Bruk

- **APM-ruta:** etter `apm install` ligg `session-start-hook` i agenten din.
- **Manuelt:** kopier `.apm/skills/session-start-hook/` til skills-mappa. Sjå
  [Last ned og last inn](../installering/manuell.md).
