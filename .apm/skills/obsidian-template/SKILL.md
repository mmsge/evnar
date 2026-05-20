---
name: obsidian-template
description: >
  Lag nye Obsidian-templatar tilpassa Markus sin vault. Bruk denne skillen kvar gong Markus bed om ein ny Obsidian-template, eit templateutkast, eller vil lage ein ny notattype i Obsidian. Triggarar inkluderer: "lag ein template", "ny template for", "Obsidian-template", "templateutkast", "templat", "notatmal". Bruk alltid denne skillen for template-arbeid — ikkje improvisér ein struktur utan han.
---

# Obsidian Template Creator

Du skal lage ein Obsidian-template tilpassa Markus sin vault og stilpreferansar. Markus skriv på nynorsk.

## Steg 1 – Still avklaringsspørsmål

Før du lagar templaten, spør om desse tinga (tilpass spørsmåla til konteksten — ikkje still spørsmål som allereie er svarte på):

1. **Kva er templaten til?** Kort beskriving av kva type notat den skal bruke til.
2. **Skal innhaldet publiserast?** (t.d. på markus.plus) — avgjer kva frontmatter-felt som trengst.
3. **Kva for hovudfelt treng han?** T.d. forfattar, artist, lokasjon, isbn, dato for hendinga osv.
4. **Kva permalink-struktur vil han ha?** T.d. `melding/bok/{{title}}` eller `reise/tog/`.
5. **Kva for tags/knappar skal stå i sjølve notatteksten?** T.d. `#melding/bok`, `#reise/tog`.

Ikkje still alle spørsmåla om det allereie er openbart frå konteksten. Vær pragmatisk.

## Steg 2 – Generer templaten

Bruk Obsidian Templater-syntaks: `{{title}}` for tittel, `{{date:FORMAT}}` for dato/tid, `{{time}}` for klokkeslett.

### Frontmatter-reglar

**For publisert innhald** (blogginnlegg, meldingar, konsert, reise som skal på nett):
```yaml
---
dato: "{{date:YYYY-MM-DD}}"
fediverse:creator: "@markus@skvip.lol"
aliases:
title:
description: [Beskriving, t.d. "Melding av «{{title}}»"]
permalink: [passande sti, t.d. melding/bok/{{title}}]
image: [URL til forsidebilde eller tomt]
publish: "true"
modified: "{{date:YYYY-MM-DD}}"
accent:
[innhaldsspesifikke felt her]
---
```

**For privat/dagleg innhald** (dagbok, grunnmur, personlege notat):
```yaml
---
aliases:
tid: "{{date:YYYY/MM/DD:HH.mm}}"
lokasjon: Bergen
tags:
  - "#{{date:YYYY/MM/DD}}"
  - "#y{{date:YYYY}}/m{{date:MM}}/d{{date:DD}}"
  - "#m{{date:MM}}/d{{date:DD}}"
  - "#d{{date:DD}}"
  - "#y{{date:YYYY}}"
  - "#m{{date:MM}}"
  - "#w{{date:WW}}"
  - "#h{{date:HH}}"
  - "#min{{date:mm}}"
  - "#{{date:dddd}}"
tidssone: "{{date:Z}}"
[andre relevante felt]
---
```

**For kreativt innhald** (dikt, manus, teikneserie) utan publisering:
```yaml
---
aliases:
---
```
Enklare frontmatter — kreative notat treng sjeldan mange metadatafelt.

### Kroppstekst-reglar

- Første linje er alltid ei overskrift: `# {{title}}` (eller `# [[{{title}}]]` for wikilink-stil)
- Tags skriv du som `#knagg/underknagg` direkte i teksten (ikkje berre i frontmatter)
- Bilete-format: `[![Alt-tekst|100]()]()` — ein klikkbar biletelenke med bredde i px
- Bruk `##` for deloverskrifter
- Hald tekst på nynorsk

### Innhaldsspesifikke felt og seksjonar

| Type | Typiske frontmatter-felt | Typiske tekstseksjonar |
|---|---|---|
| Bokmelding | forfattar, bookwyrm, isbn, språk, Antal sider, anskaffet | Melding |
| Filmmelding | språk, sett | Kort skildring, Melding |
| Konsert | artist, lokasjon | Melding, Settliste |
| Reise/tog | ingen spesielle | Reiseetappar, Kart (med iframe) |
| Dagbok | middag, humør, traff, ifjor, tidssone | (open tekst) |
| Dikt | ingen spesielle | (open tekst) |
| Teikneserie | ingen spesielle | Skildring, Mermaid-diagram eller panelstruktur |

### Kart-iframe for reisenotat
```html
<iframe src="https://embed.viaduct.world/j/NSIDl7qvLpecU4zx?layer=Topo&tabs=map,trips,stats" width="100%" height="350" style="border:0;" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade" ></iframe>
```

## Steg 3 – Lever resultatet

Skriv ut den ferdige templaten som ein kodeblokk (markdown), klar til å lime inn i Obsidian. Forklar kort kva kvart felt og kvar seksjon er til, spesielt om du har teke val som Markus burde vite om.

Tilby gjerne å justere om noko ikkje stemmer.
