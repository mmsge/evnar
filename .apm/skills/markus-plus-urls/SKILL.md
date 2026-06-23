---
name: markus-plus-urls
description: "Understand and navigate the URL structure of markus.plus so Claude can query the correct paths when searching for Markus's content. Use this skill whenever you need to look up a page on markus.plus, construct a query path, or fetch content via the markus.plus MCP tool. Trigger for any question that might involve markus.plus content: books, travel, concerts, projects, personal pages, reviews, comics, or reading logs."
---

# markus.plus — URL structure reference

markus.plus is Markus's personal Obsidian Publish site in Nynorsk. All content is available via the `markus.plus` MCP tools: `list_pages`, `get_page`, `search`, `get_frontmatter`.

---

## Top-level sections

| Path prefix | Content type |
|---|---|
| `/melding/bok/` | Book reviews |
| `/melding/film/` | Film reviews |
| `/melding/fjernsyn/` | TV reviews |
| `/melding/teater/` | Theatre reviews |
| `/lesing/` | Monthly/yearly reading logs |
| `/reisar/` | Travel writing |
| `/musikk/konsert/` | Concert notes |
| `/personar/` | Person/author pages |
| `/person/` | Alternate person path (rare) |
| `/prosjekt/` | Projects (creative, coding) |
| `/teikneseriar/` | Comics / webcomics |
| `/fritid/` | Leisure / hobby page |
| `/modelltog/` | Model trains hobby |
| `/berre-skvip/` | Private/members-only content (poems, etc.) |
| `/arskavalkade/` | Year-in-review pages |
| `/om/` | About / meta pages |
| `/meg/` | Personal pages about Markus |

---

## Section details

### `/melding/bok/` — Book reviews

- Format: `/melding/bok/<slugified-title>`
- The slug is the book title, lowercased, spaces replaced with `-`
- Special characters are kept if they appear in the title (e.g., `&`, commas, exclamation marks)
- Long titles stay long (e.g., `/melding/bok/tomorrow,-and-tomorrow,-and-tomorrow-discover-the-moving,-powerful-sunday-times-bestseller-that-everyone-is-talking-about!`)
- Some titles use Norwegian characters: `å`, `ø`, `æ` remain in slugs (e.g., `/melding/bok/få-meg-på,-for-faen`)
- The parent index page is at `/melding/bok`

**Examples:**
```
/melding/bok/septologien
/melding/bok/morgon-og-kveld
/melding/bok/the-thursday-murder-club
/melding/bok/heartstopper-volume-5
/melding/bok/om-udregning-af-rumfang-i   ← series numbered with roman numerals
/melding/bok/om-udregning-af-rumfang-6   ← or arabic numerals
```

### `/melding/film/` — Film reviews

- Format: `/melding/film/<slugified-title>`
- Subdirectories are possible for grouped films: `/melding/film/jol/a-very-jonas-christmas-movie`

**Examples:**
```
/melding/film/gondola
/melding/film/civil-war
/melding/film/victoria-må-død
/melding/film/jol/a-very-jonas-christmas-movie
```

### `/melding/fjernsyn/` — TV reviews

- Format: `/melding/fjernsyn/<show>/<season>`

**Examples:**
```
/melding/fjernsyn/doctor-who/sesong-2
/melding/fjernsyn/cammo
```

### `/lesing/` — Reading logs

- Yearly index: `/lesing/<year>` (e.g., `/lesing/2025`, `/lesing/2026`)
- Monthly log: `/lesing/<year>/<month-in-Norwegian>` 
- Norwegian month names used in paths:

| Month | Path slug |
|---|---|
| January | `januar` |
| February | `februar` |
| March | `mars` |
| April | `april` |
| May | `mai` |
| June | `juni` |
| July | `juli` |
| August | `august` |
| September | `september` |
| October | `oktober` |
| November | `november` |
| December | `desember` |

**Examples:**
```
/lesing/2025
/lesing/2025/juni
/lesing/2026/januar
```

- Top-level `/lesing` is an index of all reading content.

### `/reisar/` — Travel

- Index: `/reisar`
- Train travel: `/reisar/tog/<year>/<destination>`
- Interrail trips: `/reisar/interrail/<year>`
  - Individual legs: `/reisar/interrail/<year>/etappe-<n>`
  - City stops: `/reisar/interrail/<year>/<city-name>` (e.g., `heidelberg`, `zermatt`, `milano`, `praha`)

**Examples:**
```
/reisar/interrail/2025
/reisar/interrail/2025/etappe-3
/reisar/interrail/2025/zermatt
/reisar/interrail/2026
/reisar/tog/2025/noreg
/reisar/tog/2026/berlin
/reisar/tog/2026/københavn
```

### `/musikk/konsert/` — Concert notes

- Format: `/musikk/konsert/<YYYYMMDD>-<artist-slug>`
- Date is ISO-adjacent: 8-digit date prefix, then hyphen, then artist name slug

**Examples:**
```
/musikk/konsert/20260110-synne-sorgjerd
/musikk/konsert/20260117-janove
/musikk/konsert/20260117-ragnhild-risnes
/musikk/konsert/20260228-extra-lives
```

### `/personar/` and `/person/` — People pages

- Usually `/personar/<name-slug>` (plural form)
- A few use `/person/<name-slug>` (singular, seems to be an inconsistency)

**Examples:**
```
/personar/jon-fosse
/personar/maisie-peters
/personar/helen-kaldheim
/personar/malin-falch
/person/cerys-hafana
```

### `/prosjekt/` — Projects

- Creative projects: `/prosjekt/<project-slug>`
- Coding projects: `/prosjekt/koding/<project-slug>`

**Examples:**
```
/prosjekt/udugelege-heltar
/prosjekt/koding/del-pa-mastodon-fra-obsidian-publish
```

### `/arskavalkade/` — Year in review

- Format: `/arskavalkade/<year>`

**Examples:**
```
/arskavalkade/2025
```

### `/teikneseriar/` — Comics

- Index: `/teikneseriar`
- Individual comics: `/teikneseriar/<comic-slug>`

**Examples:**
```
/teikneseriar/havfrue
/teikneseriar/heisen
/teikneseriar/fleire-figurar
```

### `/berre-skvip/` — Private / members content

- Poems and personal writing visible only to skvip.lol members
- Format: `/berre-skvip/<category>/<slug>`

**Example:**
```
/berre-skvip/dikt/mamma-er-dod
```

### `/om/` — About / meta pages

```
/om/tankehav
/om/tankekart
```

### `/meg/` — Personal pages

```
/meg
/meg/some
```

---

## Querying tips

- **To find a book review**, construct: `/melding/bok/<title-slug>` — if unsure of exact slug, use `search` with the book title.
- **To find a reading month**, use `/lesing/<year>/<norwegian-month>`.
- **To find a concert**, search by artist name or construct `/musikk/konsert/<date>-<artist>`.
- **To find a travel log**, try `/reisar/interrail/<year>` or `/reisar/tog/<year>/<destination>`.
- **When the exact slug is unknown**, always prefer `search` with keywords over guessing the path.
- **`get_frontmatter` is broken** — do not rely on it. Use `get_page` to retrieve content and metadata inline.

---

## Anomalies to be aware of

- One page has a broken path with spaces: `/St. Gallen` and `/Odin Helgheim` — these appear to be Obsidian Publish edge cases where internal links didn't resolve to clean slugs.
- Some book slugs include punctuation from long subtitles — always try `search` first if the slug is uncertain.
- `/melding/bok/` has an empty-slug entry (`/melding/bok/`) — this is the section index.
