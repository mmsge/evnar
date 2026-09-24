# evnar

Sentral APM-pakke for Markus sine evnar, instruksjonar, prompts,
agentdefinisjonar, hooks og MCP-serverar.

Repoet brukar [Agent Package Manager](https://microsoft.github.io/apm/) som
kjeldeformat. Alt du redigerer ligg under `.apm/`; klientspesifikke mapper som
`.claude/`, `.codex/`, `.github/`, `.cursor/` og `.agents/skills/` blir laga av
APM.

## Installasjon

Installer APM og køyr:

```bash
git clone https://github.com/mmsge/evnar.git
cd evnar
apm install --target all,agent-skills
```

Du kan og bruke wrapperen:

```bash
./install.sh
```

Wrapperen krev APM og køyrer same installasjon med standardmålet
`all,agent-skills`.

## Last ned enkeltevner

Kvar evne har si eiga utgåve på
[Releases](https://github.com/mmsge/evnar/releases), med eigen tagg på forma
`<evne>-v<versjon>`. Det er utgåvesida du deler når du vil senda éi evne til
nokon:

<https://github.com/mmsge/evnar/releases/tag/offshoot-v1.2.0>

Du treng verken APM eller klone av repoet for å bruke ei enkelt evne:

```bash
curl -LO https://github.com/mmsge/evnar/releases/download/offshoot-v1.2.0/offshoot.skill
unzip offshoot.skill -d ~/.claude/skills/     # gjev ~/.claude/skills/offshoot/SKILL.md
```

Arkivet inneheld mappa til evna, så du pakkar det rett ut der evnene bur. Bruk
`.claude/skills/` i eit prosjekt om evna berre skal gjelda der.

Kvar evne finst i to utgåver med same innhald: `.skill` og `.zip`. Bruk `.zip`
når du lastar opp til claude.ai, som berre godtek det filnamnet. `SHA256SUMS`
ligg ved for verifisering.

Ein `vX.Y.Z`-tagg på repoet lagar i tillegg eit samla øyeblikksbilete med
`evnar-all-skills.zip` og `skills.json`, for deg som vil ha alt på ein gong.

## Versjonering

Versjonen til ei evne står i frontmatteren i `SKILL.md`, og det er han som
styrer utgjevinga:

```yaml
---
name: offshoot
version: 1.0.0
description: ...
---
```

Bump versjonen når du endrar evna, etter semver: `Z` for ein retting, `Y` for
ny funksjonalitet som ikkje bryt noko, `X` for ei endring som bryter. Neste
push til `hovud` lagar utgåva. Lèt du versjonen stå, skjer ingenting, og ei
publisert utgåve blir aldri skriven over. Ein pull request som endrar ei evne
utan å bumpa versjonen feiler i CI, nettopp for at endringa ikkje skal bli
liggjande uutgjeven.

Pakkinga skjer i [`pack-skills.yml`](.github/workflows/pack-skills.yml). Du kan
køyre same bygg lokalt:

```bash
pip install pyyaml
python3 .github/scripts/pack_skills.py
```

## Innhald

| Type | Plassering |
|---|---|
| Evner | `.apm/skills/<namn>/SKILL.md` |
| Instruksjonar | `.apm/instructions/*.md` |
| Prompts | `.apm/prompts/*.prompt.md` |
| Agentar | `.apm/agents/*.agent.md` |
| Hooks | `.apm/hooks/` |
| Delt kontekst | `.apm/context/` |
| MCP-serverar | `dependencies.mcp` i `apm.yml` |

## Evner

Versjonsnummeret lenkjer til utgåvesida for evna.

| Evne | Versjon | Beskriving |
|---|---|---|
| [`agent-activity-log`](.apm/skills/agent-activity-log/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/agent-activity-log-v1.0.0) | Hald ein tidsstempla aktivitetslogg som publisert artefakt medan ein agent arbeider utan tilsyn |
| [`books`](.apm/skills/books/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/books-v1.0.0) | Søk i lesehistorikk frå StoryGraph og Bookwyrm |
| [`doctor-who`](.apm/skills/doctor-who/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/doctor-who-v1.0.0) | Slå opp, svar på og diskuter alt om Doctor Who |
| [`favicon`](.apm/skills/favicon/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/favicon-v1.0.0) | Set opp favicon rett for eit webprosjekt, frå botnen eller som opprydding |
| [`git`](.apm/skills/git/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/git-v1.0.0) | Git-arbeidsflyt frå lokal commit til pull request, kodegjennomgang og CI |
| [`lastfm-scrobble-report`](.apm/skills/lastfm-scrobble-report/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/lastfm-scrobble-report-v1.0.0) | Lag ein Last.fm-scrobblerapport for ein artist, som PDF og CSV |
| [`mastodon`](.apm/skills/mastodon/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/mastodon-v1.0.0) | Hent og vis siste innlegg frå @markus@skvip.lol |
| [`new-project-scaffold`](.apm/skills/new-project-scaffold/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/new-project-scaffold-v1.0.0) | Set opp nye programvareprosjekt med komplett, produksjonsklar struktur |
| [`obsidian-template`](.apm/skills/obsidian-template/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/obsidian-template-v1.0.0) | Lag nye Obsidian-templatar tilpassa Markus sin vault |
| [`offshoot`](.apm/skills/offshoot/SKILL.md) | [1.2.0](https://github.com/mmsge/evnar/releases/tag/offshoot-v1.2.0) | Spinn arbeid ut i ei eiga økt med ein brief som held på rammene |
| [`offshoot-portable`](.apm/skills/offshoot-portable/SKILL.md) | [1.1.0](https://github.com/mmsge/evnar/releases/tag/offshoot-portable-v1.1.0) | Same som `offshoot`, men for Codex, Copilot, ChatGPT og claude.ai/code òg |
| [`project-review`](.apm/skills/project-review/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/project-review-v1.0.0) | Analyser eit prosjekt og lag ei rangert liste med forbetringsframlegg |
| [`repo-settings`](.apm/skills/repo-settings/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/repo-settings-v1.0.0) | Sett standardinnstillingar på eit GitHub-repo |
| [`session-start-hook`](.apm/skills/session-start-hook/SKILL.md) | [1.0.0](https://github.com/mmsge/evnar/releases/tag/session-start-hook-v1.0.0) | Lag SessionStart-hooks for Claude Code på nettet |

## Nyttige kommandoar

```bash
apm targets
apm install --target all,agent-skills --dry-run
apm install --target all,agent-skills
apm audit
apm pack
```

Sjå [docs/APM.md](docs/APM.md) for repo-spesifikke notat, og
[docs/offshoot-portable-install.md](docs/offshoot-portable-install.md) for installasjonsstiane
til `offshoot-portable` i dei ulike klientane.
