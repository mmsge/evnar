---
title: APM-ruta
sidebar_label: APM-ruta
sidebar_position: 1
---

# APM-ruta

Dette er den tilrådde måten når du vil ha **alle** skillane i `evnar` installerte
på ein gong — og halde dei oppdaterte seinare med éin kommando.

## 1. Installer APM

[Agent Package Manager](https://microsoft.github.io/apm/) er pakkehandteraren
som les `.apm/`-kjelda og legg skillane ut til klientmappene. Installer han frå
oppstraumsprosjektet og sjekk at `apm` ligg på `PATH`:

```bash
apm --version
```

## 2. Klon og installer

```bash
git clone https://github.com/mmsge/evnar.git
cd evnar
apm install --target all,agent-skills
```

Dette legg skillane ut til **alle** klientane som er deklarerte i `apm.yml`
(`copilot`, `claude`, `cursor`, `codex`, `gemini`, `opencode`, `windsurf`) pluss
det portable `agent-skills`-formatet under `.agents/skills/`.

## 3. Eller bruk wrapperen

Repoet har eit lite skal-skript som kallar same kommando med standardmålet
`all,agent-skills`:

```bash
./install.sh
```

Wrapperen krev at `apm` ligg på `PATH` — elles avsluttar han med ein feil
(`exit 127`). Du kan sende eigne flagg vidare:

```bash
./install.sh --target claude,agent-skills   # berre Claude + portable skills
./install.sh --dry-run                       # vis kva som ville skjedd
```

## Velje mål (targets)

Vil du ikkje ha alle klientane, vel eitt eller fleire mål med komma:

```bash
apm install --target claude,agent-skills
```

## Nyttige kommandoar

```bash
apm targets                                  # list tilgjengelege mål
apm install --target all,agent-skills --dry-run   # førehandsvis
apm install --target all,agent-skills        # installer / oppdater
apm audit                                    # sjekk pakka
apm pack                                      # pakk for distribusjon
```

:::note
Vil du heller berre prøve éin enkelt skill utan å installere APM? Sjå
[Last ned og last inn](./manuell.md).
:::
