---
title: Last ned og last inn
sidebar_label: Last ned og last inn
sidebar_position: 2
---

# Last ned og last inn

Treng du ikkje heile pakka — berre éin skill? Du treng **ikkje** APM i det heile
tatt. Kvar skill er ei sjølvstendig mappe, så du kan laste han ned og legge han
rett inn i skills-mappa til agenten din.

## 1. Last ned skill-mappa

Hent mappa `.apm/skills/<namn>/` frå repoet. To enkle måtar:

```bash
# Klon heile repoet og kopier ut éin skill
git clone https://github.com/mmsge/evnar.git
cp -r evnar/.apm/skills/git ~/Downloads/
```

…eller last ned mappa direkte frå GitHub-grensesnittet.

:::caution Ta med heile mappa
Mange skills har `references/`, `scripts/` eller `assets/` ved sida av
`SKILL.md`. Kopier **heile** skill-mappa, ikkje berre `SKILL.md` — elles manglar
skillen oppslagsfilene og hjelpescripta sine.
:::

## 2. Legg mappa i skills-katalogen

For **Claude Code** legg du skill-mappa ein av desse stadene:

| Stad | Sti | Gjeld |
|---|---|---|
| Personleg | `~/.claude/skills/<namn>/` | alle prosjekta dine |
| Per prosjekt | `<prosjekt>/.claude/skills/<namn>/` | berre det eine prosjektet |

```bash
mkdir -p ~/.claude/skills
cp -r evnar/.apm/skills/git ~/.claude/skills/git
```

Andre klientar har sine eigne mapper (t.d. `.cursor/`); APM sitt
`agent-skills`-mål skriv eit portabelt `.agents/skills/`-oppsett som passar dei
fleste.

## 3. Last inn

Agenten oppdagar skillen automatisk frå `name` + `description` i `SKILL.md`.
Start agenten på nytt om han allereie køyrde, og be om noko som matchar
triggerane til skillen (sjå kvar [skill-side](../skills/oversikt.md)).

## Føresetnader per skill

Skills som berre er instruksjonar (t.d. `obsidian-template`, `git`,
`project-review`) treng ingenting ekstra. Skills med script treng køyretida og
pakkane sine — døme:

- [`lastfm-scrobble-report`](../skills/lastfm-scrobble-report.md) — Python +
  `reportlab`, `matplotlib`, `pillow`
- [`repo-settings`](../skills/repo-settings.md) — `gh` CLI + `jq`
- [`mastodon`](../skills/mastodon.md) — API-token (ligg i ei referansefil)

Kvar skill-side listar føresetnadene sine.
