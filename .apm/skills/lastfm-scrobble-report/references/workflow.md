# Workflow Reference

## Finding an artist's full discography

1. Call `get_artist_info(artist)` — check the description and tags for hints about
   how many albums exist.
2. Web-search `"<artist> discography studio albums"` to get a complete album list
   with release years. Note any deluxe editions.
3. For each album, note:
   - Standard track count
   - Whether a Deluxe/Extended edition exists with bonus tracks
   - Pre-release singles (released before the album but included on it)
   - Standalone singles released between albums (not on any album)

## Calling get_album_info

```
get_album_info(artist="Artist Name", album="Album Title", username="lastfm_username")
```

- Returns a track list and **your** play count for the album as a whole.
- The track list may be **incomplete** — Last.fm often only lists 10 tracks even
  for longer albums. Always cross-check against the known full track count.
- The Deluxe album entry often only shows the base tracks too — fetch bonus tracks
  individually.

## Calling get_track_info

```
get_track_info(artist="Artist Name", track="Track Title", username="lastfm_username")
```

- Returns your personal play count for that specific track.
- Use this for every track not covered by the album entry.
- Use this for all deluxe bonus tracks, pre-release singles, and between-album singles.

## Avoiding double-counting

The trickiest part. Rules:

1. **Take the album-tagged total** (`get_album_info` → `your plays`) as the
   authoritative figure for the base album tracks.
2. For the Deluxe edition, `get_album_info` on the Deluxe listing may show a
   **separate** play count — but it usually covers the same base tracks. Don't
   add the Deluxe total on top of the standard total. Instead:
   - Use the **standard** album total for the 10 base tracks
   - Fetch the **bonus tracks individually** and add those
3. Pre-release singles: if the track appears on the album AND was a single, its
   plays are included in the album total. Don't add separately.
4. Standalone singles (not on any album): always add individually.

## Estimating plays for unresolvable tracks

When a track returns 0 due to apostrophe encoding (see known_issues.md):
- The plays are included in the album-tagged total
- Estimate by: `album_total - sum(all resolvable tracks in album)`
- Label as "⚠ unresolvable (est.)" in the table/CSV

## Annotating tracks

Use these standard note values in the data:

| Note string | Meaning |
|---|---|
| `""` (empty) | Standard album track, resolved |
| `"Pre-release single"` | Released as single before album |
| `"Deluxe bonus"` | Only on deluxe edition |
| `"Single (not on album)"` | Standalone single, never on a studio album |
| `"API encoding issue"` | Curly apostrophe — plays unresolvable individually |

## Presenting results to the user

Always present both files together:
```python
present_files([pdf_path, csv_path])
```

After presenting, briefly note:
- Top track (most plays)
- Any unresolvable tracks and how many plays are estimated to be in them
- For incomplete albums (like Florescence), note how many tracks remain
