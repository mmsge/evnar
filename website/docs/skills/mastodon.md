---
title: mastodon
---

# `mastodon`

> Hent og vis dei siste Mastodon-innlegga til Markus frå @markus@skvip.lol.

## Kva han gjer

Hentar statusane til Markus via Mastodon-API-et (skvip.lol-instansen), slår opp
konto-ID, strippar HTML og formaterer innlegga som lesbar tekst med dato, boosts
og favorittar. Standard-grense er 5 innlegg.

## Når han slår til

Når Markus spør om Mastodon-innlegga sine, toots, aktivitet, kva han har posta i
det siste, eller fediverse-innlegga sine. Skillen brukar API-et — han
web-søkjer eller gjettar **aldri** på innhaldet.

## Kva som følgjer med

- `SKILL.md` med ei referansefil som inneheld API-token

## Føresetnader

Eit Mastodon-API-token (ligg i den medfølgjande referansefila).

## Bruk

- **APM-ruta:** etter `apm install` ligg `mastodon` i agenten din.
- **Manuelt:** kopier `.apm/skills/mastodon/` til skills-mappa. Sjå
  [Last ned og last inn](../installering/manuell.md).
