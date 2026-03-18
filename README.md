# evnar

Samling av Markus sine evnar (skills) for Claude Code.

## Installasjon

Klona repoet og køyr installasjonsskripta:

```bash
git clone https://github.com/mmsge/evnar.git
cd evnar
./install.sh
```

Skripta symlenkar kvar evne til `~/.claude/skills/` slik at Claude Code
finn dei automatisk. Allereie installerte evner blir ikkje overskrivne
— køyr med `--force` for å oppdatere:

```bash
./install.sh --force
```

## Evner

| Evne | Beskriving |
|---|---|
| [`obsidian-template`](skills/obsidian-template/SKILL.md) | Lag nye Obsidian-templatar tilpassa Markus sin vault |
| [`mastodon`](skills/mastodon/SKILL.md) | Hent og vis siste innlegg frå @markus@skvip.lol |
| [`new-project-scaffold`](skills/new-project-scaffold/SKILL.md) | Set opp nye programvareprosjekt med komplett, produksjonsklar struktur |
| [`books`](skills/books/SKILL.md) | Søk i lesehistorikk frå StoryGraph og Bookwyrm |
| [`doctor-who`](skills/doctor-who/SKILL.md) | Slå opp, svar på og diskuter alt om Doctor Who |
| [`session-start-hook`](skills/session-start-hook/SKILL.md) | Lag SessionStart-hooks for Claude Code på nettet |

## Struktur

```
skills/
  <evne-namn>/
    SKILL.md        # Hovudfil — instruksjonar og beskriving for Claude
    references/     # (valfritt) Referansefiler som evna les frå
```

Kvar evne ligg i si eiga mappe med ei `SKILL.md`-fil. Referansefiler
(t.d. API-token, faktaark) kan leggjast i ei `references/`-undermappe
ved sidan av `SKILL.md`.
