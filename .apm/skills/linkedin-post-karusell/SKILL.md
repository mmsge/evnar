---
name: linkedin-post-karusell
description: >
  Lag eit LinkedIn-innlegg med tilhøyrande PDF-karusell i Markus sin stil — nynorsk, hook-først, kort post som peikar på ein 4–6 sliders karusell med djup grøn bakgrunn, lime-aksent, store kvite Lato Black-overskrifter, line-ikon, bilete, progress-bar og footer (Bolk-stilen). Bruk denne skillen kvar gong Markus vil dele eit prosjekt, ein observasjon eller eit funn på LinkedIn. Triggarar inkluderer: "lag ein linkedin-post", "linkedin karusell", "post om [prosjekt]", "skriv ein post", "karusell til linkedin", "linkedin-innlegg om". Bruk han òg når Markus vil "workshoppe" eit post-utkast — han pleier å laga karusell saman med teksten. Bruk alltid denne skillen for LinkedIn-arbeid — ikkje improvisér ein struktur utan han.
---

# LinkedIn-post + karusell (Markus sin stil)

Hjelp Markus laga eit kort LinkedIn-innlegg på nynorsk med ein tilhøyrande PDF-karusell. Resultatet skal sjå ut som Bolk-malen: **djup skog-grøn bakgrunn**, **lime-grøn aksent**, store **kvite Lato Black**-overskrifter som fyller plassen, **line-ikon** og **bilete** framfor tom plass, progress-bar oppe og prosjektnamn + sidetal i botnen. Lyse **krem-kort** ber innhald som sjekklister og diagram.

## Steg 1 — Avklar konteksten

Still desse spørsmåla før du skriv noko (hopp over dei som er svarte allereie):

1. **Kva er prosjektet/observasjonen?** Kort skildring av kva han vil dele.
2. **Kva vinkel skal posten ha?** Personleg nysgjerrigheit, byggje-historia, funn frå data, eller verktøy-demo?
3. **Kva publikum?** Mixed (default), tekniske kollegaer, eller leiarar/ikkje-tekniske.
4. **Kor mange slides i karusellen?** 4–6 etter behov.
5. **Finst det bilete eller skjermbilete?** Filsti — biletet blir helst eit halvsides avrunda foto (Bolk s1). Elles kan vi bruka eit line-ikon eller rendre eit diagram frå data.
6. **URL/CTA?** Lenke til appen/koden/demoen.

Les `references/voice-guide.md` for å fanga opp stilen før du skriv. Den fila har eksempel på opnarar, struktur, hashtag-bruk og karusell-stilen.

## Steg 2 — Skriv post-teksten

Følg desse prinsippa (sjå `references/voice-guide.md` for fleire eksempel):

- **Eittsetnings-hook**. Første line skal skapa undring — ikkje skildra prosjektet.
- **Korte avsnitt**. Eitt avsnitt per tanke. Sjeldan meir enn 2–3 setningar.
- **Historie-bogen**: personleg observasjon → kva eg gjorde → kva eg fann → CTA.
- **"Bygd raskt med språkmodellar, men sjølve appen brukar ikkje KI"** — bruk når det stemmer.
- **Eitt konkret funn eller tal** for å hooka lesaren til å swipe karusellen.
- **Hashtags på siste line**, 3–5 stk. `#KI`, ikkje `#AI`.

Teksten ber ikkje den visuelle vekta — karusellen gjer det.

## Steg 3 — Designa karusell-strukturen

Karusellen følgjer ein fast historie-boge. Tilpass talet på slides (4–6):

| Slide | Kicker (lite, lyst, øvst) | Funksjon | Typisk visuelt |
|------|----------------------------|----------|----------------|
| 1 | EI LITA HISTORIE | Hook — kvifor begynte du å lure? | `image` (halvside-foto) |
| 2 | KVA EG OPPDAGA | Problemet eller oppdaginga | `icon` |
| 3 | SÅ EG LAGA NOKO | Bygginga | `step_cards` / `image` |
| 4 | KVA EG FANN / KVA STRAUMANE VISER | Konkrete funn | `stat_cards` / `sankey` |
| 5 | ETTER KVAR ØKT | Oppfølgingar (valfri) | `checklist` |
| 6 | PRØV DEN SJØLV / OG NO? | CTA med URL | `url_cta` |

Kvar slide har:

- **Kicker** — lite, lyst grønt, store bokstavar med ekstra spacing, og ein kort lime-strek under.
- **Stor overskrift** — Lato Black, kvit, fyller breidda. `title_size` i px (~96–128). Bruk `\n` for manuelle linjeskift — det er viktig for typografien.
- **Underordna tekst** (valfri) — lys grøn, kortfatta. `sub` kan òg ha `\n`.
- **Visuelt element** — sjå typane under.

Designprinsipp frå Bolk: **store overskrifter, lite tom plass, ikon/bilete framfor luft.** Halds overskrifta til 2–3 liner så ho ikkje kolliderer med eit `pos:right`-ikon.

## Steg 4 — Bygg karusell-konfigurasjonen

Lag ein JSON-fil som skildrar slidene. Sjå `assets/example_config.json` for full struktur. Kort schema:

```json
{
  "project": "Prosjektnamn · open source",
  "footnote": "personleg notat",
  "out": "namn-på-pdf.pdf",
  "slides": [
    {
      "kicker": "EI LITA HISTORIE",
      "title": "Hook over\nfleire liner.",
      "sub": "Valfri undertekst.",
      "title_size": 118,
      "visual": { "type": "...", ... }
    }
  ]
}
```

### Visuelle typar

- `{"type": "none"}` — berre tekst (overskrifta ber slida).
- `{"type": "image", "path": "foto.jpg", "mode": "halfpage|fullbleed|contained", "caption": "..."}` — foto. `halfpage` (default) = stort avrunda foto i nedre halvdel (Bolk s1). `fullbleed` = foto fyller heile slida med grøn scrim bak teksten. `caption` gjev ei lita etikett-brikke.
- `{"type": "icon", "name": "notes", "pos": "right|center", "size": 320, "frame": false}` — stort outline line-ikon. `pos:right` legg det ved sida av overskrifta (Bolk s2). Tilgjengelege namn: `notes, train, map, code, chart, database, broadcast, book, mic, bulb, gear, check, globe, calendar`.
- `{"type": "checklist", "header": "Oppfølgingar", "sub": "...", "items": [{"text": "...", "done": true}, ...]}` — krem-kort med avkryssingsboksar; ferdige punkt får lime-hake og gjennomstreking, og talet (t.d. 2/6) blir rekna ut automatisk (Bolk s3).
- `{"type": "step_cards", "cards": [{"label": "Steg", "title": "1", "sub": "..."}], "arrows": true}` — rad med grøne kort og lime-piler imellom.
- `{"type": "stat_cards", "cards": [{"big": "342", "line1": "...", "line2": "...", "color": "lime"}]}` — tal-kort (1 rad ved ≤2 kort, 2×2 ved 3–4). `color`: `lime | white | cream | mute`.
- `{"type": "url_cta", "label": "...", "url": "...", "lines": ["...", "..."], "cta": "→ ..."}` — avsluttande mørkt panel (Bolk s4).
- `{"type": "sankey", "data_path": "data.json", "years": [...], "threshold": 0.5, "caption": "..."}` — fleirstegs straum-diagram på eit krem-kort.

Bilete- og data-stiar er relative til **konfigfila**.

## Steg 5 — Køyr generatoren

```bash
python3 scripts/build_carousel.py <config.json>            # → out-stien i configen
python3 scripts/build_carousel.py <config.json> --out x.pdf
```

Generatoren rendrar HTML/CSS til PDF med **wkhtmltopdf** (ein ekte WebKit-motor — inga nettlesar-nedlasting, fungerer offline). Native lerret er 1080×1350 px (4:5).

**Skrift:** karusellen brukar **Lato** (Black/Bold/Regular), bundla i `assets/fonts/`. Finst ikkje TTF-ane der, fell han tilbake på systemets sans og skriv ei åtvaring (layouten er lik, men overskriftene ser ikkje endelege ut). Hent skriftene med `bash assets/fonts/fetch-fonts.sh` (treng nett). Sjå `assets/fonts/README.md`.

## Steg 6 — Lever produktet

1. Skriv post-teksten til ei `linkedin-post.md`-fil i prosjektmappa.
2. Skriv karusell-PDF-en til same mappe.
3. Bruk `present_files` til å syna begge filene.

Til slutt: peik på ting som bør sjekkast (URL-stavemåte, repo-namn, lenkjer som ikkje finst enno), men ikkje overstyr produktet med caveats.

## Referansar

- `references/voice-guide.md` — Markus sin LinkedIn-stemme + karusell-stilen, med eksempel
- `assets/example_config.json` — Komplett karusell-konfig (køyrbar demo)
- `assets/fonts/` — Lato (bundla) + `fetch-fonts.sh`
- `scripts/build_carousel.py` — PDF-generatoren (HTML/CSS → wkhtmltopdf, Bolk-tema)
