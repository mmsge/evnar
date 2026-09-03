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

Kvar evne blir pakka som eit sjølvstendig arkiv og lagt ut på
[Releases](https://github.com/mmsge/evnar/releases). Du treng verken APM eller
klone av repoet for å bruke ei enkelt evne.

```bash
# alltid ferskaste versjon
curl -LO https://github.com/mmsge/evnar/releases/download/latest/git.skill

# ein fast versjon
curl -LO https://github.com/mmsge/evnar/releases/download/v0.1.0/git.skill
```

Arkivet inneheld mappa til evna, så du pakkar det rett ut der evnene bur:

```bash
unzip git.skill -d ~/.claude/skills/     # gjev ~/.claude/skills/git/SKILL.md
```

Kvar evne finst i to utgåver med same innhald: `.skill` og `.zip`. Bruk
`.zip` når du lastar opp til claude.ai, som berre godtek det filnamnet.
`evnar-all-skills.zip` inneheld alle evnene, og `skills.json` og `SHA256SUMS`
ligg ved for skripting og verifisering.

Pakkinga skjer i [`pack-skills.yml`](.github/workflows/pack-skills.yml). Kvar
push til `hovud` friskar opp `latest`, og ein `vX.Y.Z`-tagg lagar ei permanent
utgåve. Du kan køyre same bygg lokalt:

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
