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

| Evne | Beskriving |
|---|---|
| [`obsidian-template`](.apm/skills/obsidian-template/SKILL.md) | Lag nye Obsidian-templatar tilpassa Markus sin vault |
| [`mastodon`](.apm/skills/mastodon/SKILL.md) | Hent og vis siste innlegg frå @markus@skvip.lol |
| [`new-project-scaffold`](.apm/skills/new-project-scaffold/SKILL.md) | Set opp nye programvareprosjekt med komplett, produksjonsklar struktur |
| [`books`](.apm/skills/books/SKILL.md) | Søk i lesehistorikk frå StoryGraph og Bookwyrm |
| [`doctor-who`](.apm/skills/doctor-who/SKILL.md) | Slå opp, svar på og diskuter alt om Doctor Who |
| [`session-start-hook`](.apm/skills/session-start-hook/SKILL.md) | Lag SessionStart-hooks for Claude Code på nettet |

## Nyttige kommandoar

```bash
apm targets
apm install --target all,agent-skills --dry-run
apm install --target all,agent-skills
apm audit
apm pack
```

Sjå [docs/APM.md](docs/APM.md) for repo-spesifikke notat.
