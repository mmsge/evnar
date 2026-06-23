# Data Schema

The `generate_report.py` script accepts a single `report_data` dict with this structure.

## Top-level schema

```python
report_data = {
    "artist":   "Artist Name",          # str — display name
    "username": "lastfm_username",      # str
    "date":     "25 March 2026",        # str — generation date
    "albums": [                         # list of AlbumData dicts (see below)
        ...
    ]
}
```

## AlbumData

```python
{
    "title":        "Album Title",       # str — display title (e.g. "The Good Witch")
    "year":         2023,                # int
    "album_total":  2709,                # int — Last.fm album-tagged play count
                                         #        (use 0 if unavailable)
    "color":        "#00b894",           # str — hex colour for this album's charts
                                         #        (omit to auto-assign from palette)
    "tracks": [                          # list of TrackData dicts
        ...
    ]
}
```

## TrackData

```python
{
    "number":  1,                        # int or str — track number on album
                                         #   use "—" for standalone singles
    "title":   "Lost the Breakup",       # str
    "plays":   1440,                     # int — your scrobbles; use None if unresolvable
    "note":    "Pre-release single",     # str — see workflow.md for standard values
                                         #   use "" for a plain album track
}
```

## Note values (standard)

| Value | Meaning |
|-------|---------|
| `""` | Standard album track |
| `"Pre-release single"` | Released as single before album, included on album |
| `"Deluxe bonus"` | Only on deluxe edition |
| `"Single (not on album)"` | Standalone single, not on any studio album |
| `"API encoding issue"` | Curly apostrophe — plays unresolvable individually |

## Full example

```python
report_data = {
    "artist":   "Maisie Peters",
    "username": "mvrkws",
    "date":     "25 March 2026",
    "albums": [
        {
            "title":       "You Signed Up for This",
            "year":        2021,
            "album_total": 1509,
            "tracks": [
                {"number": 1,  "title": "You Signed Up for This",    "plays": 99,   "note": ""},
                {"number": 2,  "title": "I'm Trying (Not Friends)",  "plays": None, "note": "API encoding issue"},
                {"number": 3,  "title": "John Hughes Movie",         "plays": 102,  "note": "Pre-release single"},
                {"number": 4,  "title": "Outdoor Pool",              "plays": 101,  "note": ""},
                {"number": 5,  "title": "Love Him I Don't",          "plays": None, "note": "API encoding issue"},
                {"number": 6,  "title": "Psycho",                    "plays": 112,  "note": "Pre-release single"},
                {"number": 7,  "title": "Boy",                       "plays": 100,  "note": ""},
                {"number": 8,  "title": "Hollow",                    "plays": 104,  "note": ""},
                {"number": 9,  "title": "Villain",                   "plays": 99,   "note": ""},
                {"number": 10, "title": "Brooklyn",                  "plays": 102,  "note": "Pre-release single"},
                {"number": 11, "title": "Elvis Song",                "plays": 98,   "note": ""},
                {"number": 12, "title": "Talking to Strangers",      "plays": 138,  "note": ""},
                {"number": 13, "title": "Volcano",                   "plays": 110,  "note": ""},
                {"number": 14, "title": "Tough Act",                 "plays": 130,  "note": ""},
            ]
        },
        {
            "title":       "The Good Witch",
            "year":        2023,
            "album_total": 2709,
            "tracks": [
                {"number": 1,   "title": "The Good Witch",                            "plays": 229,  "note": ""},
                {"number": 2,   "title": "Coming of Age",                             "plays": 212,  "note": ""},
                {"number": 3,   "title": "Watch",                                     "plays": 210,  "note": ""},
                {"number": 4,   "title": "Body Better",                               "plays": 280,  "note": "Pre-release single"},
                {"number": 5,   "title": "Want You Back",                             "plays": 211,  "note": ""},
                {"number": 6,   "title": "The Band and I",                            "plays": 218,  "note": ""},
                {"number": 7,   "title": "You're Just a Boy (And I'm Kinda the Man)", "plays": None, "note": "API encoding issue"},
                {"number": 8,   "title": "Lost the Breakup",                          "plays": 1440, "note": "Pre-release single"},
                {"number": 9,   "title": "Wendy",                                     "plays": 216,  "note": ""},
                {"number": 10,  "title": "Run",                                       "plays": 213,  "note": ""},
                {"number": 11,  "title": "Holy Revival",                              "plays": 259,  "note": "Deluxe bonus"},
                {"number": 12,  "title": "Yoko",                                      "plays": 108,  "note": "Deluxe bonus"},
                {"number": 13,  "title": "The Song",                                  "plays": 304,  "note": "Deluxe bonus"},
                {"number": 14,  "title": "Guy On A Horse",                            "plays": 105,  "note": "Deluxe bonus"},
                {"number": 15,  "title": "Truth Is",                                  "plays": 106,  "note": "Deluxe bonus"},
                {"number": 16,  "title": "The Last One",                              "plays": 108,  "note": "Deluxe bonus"},
                {"number": "—", "title": "Two Weeks Ago",                             "plays": 233,  "note": "Single (not on album)"},
            ]
        },
        {
            "title":       "Florescence",
            "year":        2026,
            "album_total": 0,
            "tracks": [
                {"number": 2, "title": "Audrey Hepburn",           "plays": 312, "note": "Pre-release single"},
                {"number": 3, "title": "Say My Name In Your Sleep","plays": 168, "note": "Pre-release single"},
                {"number": 8, "title": "My Regards",               "plays": 357, "note": "Pre-release single"},
                {"number": 9, "title": "You You You",               "plays": 301, "note": "Pre-release single"},
            ]
        },
    ]
}
```
