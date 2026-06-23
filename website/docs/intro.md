---
title: Kva er evnar?
sidebar_label: Introduksjon
sidebar_position: 1
---

# evnar

`evnar` er den sentrale **APM-pakken** til Markus — ei kuratert samling av
agent-_skills_ (evner), instruksjonar, prompts, agentdefinisjonar, hooks og
MCP-server-deklarasjonar. Skillane kan installerast i Claude, Copilot, Cursor,
Codex, Gemini, OpenCode og Windsurf, eller som frittståande agent-skills.

Pakka brukar [Agent Package Manager (APM)](https://microsoft.github.io/apm/) som
kjeldeformat. Alt som er redigerbart ligg under `.apm/`; klientmappene
(`.claude/`, `.cursor/`, `.agents/skills/` osv.) blir _genererte_ av APM og er
ikkje i git.

## Kva er ein «skill»?

Ein skill er ei sjølvstendig mappe med ei `SKILL.md`-fil. Frontmatteren har eit
`name` og ein `description`; agenten les `description` og slår på skillen
automatisk når oppgåva passar. Ein skill kan òg ha:

- `references/` — djupare kontekst (oppslagstabellar, stilguidar, tekniske notat)
- `scripts/` — køyrbare hjelpescript
- `assets/` — malar, døme-data, font-filer

## To måtar å installere på

| Rute | Når du vel han |
|---|---|
| [**APM-ruta**](./installering/apm.md) | Du vil ha _alle_ skillane på ein gong og halde dei i synk |
| [**Last ned og last inn**](./installering/manuell.md) | Du vil berre prøve _éin_ skill, utan å installere APM |

## Kva ligg i pakka?

**11 skills** — frå Doctor Who-oppslag og git-arbeidsflyt til prosjekt-scaffolding
og favicon-oppsett. Sjå [heile katalogen](./skills/oversikt.md).

:::tip
Vil du forstå korleis `.apm/`-treet heng saman og kva kommandoar som finst? Sjå
[APM-kjeldeformatet](./apm-format.md).
:::
