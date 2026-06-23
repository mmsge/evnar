# Known Last.fm API Issues

## 1. Curly apostrophe encoding (most common issue)

### What happens
Some track names use a curly/typographic apostrophe (`'` = U+2019) in Last.fm's
database, for example:
- `I'm Trying (Not Friends)` → stored as `I\u2019m Trying (Not Friends)`
- `Love Him I Don't` → stored as `Love Him I Don\u2019t`
- `You're Just a Boy (And I'm Kinda the Man)` → multiple curly apostrophes

When `get_track_info` is called with a straight apostrophe (`'`), the API returns
0 plays even though the plays exist. The Last.fm MCP tool normalises the apostrophe
before sending the request, so there is no workaround via the tool itself.

### How to identify it
- `get_track_info` returns `your plays: 0` but:
  - The track is well-known and you'd expect plays
  - The album-tagged total is higher than the sum of individually resolved tracks
- The Last.fm web URL for the track contains `%E2%80%99` (URL-encoded U+2019)

### Mitigation
1. After fetching all resolvable tracks, compute:
   `unresolved_plays = album_total - sum(resolvable_track_plays)`
2. For each ⚠ track, annotate as `"API encoding issue"` in the table
3. Optionally: user can verify exact counts by checking the Last.fm mobile app
   (Library → Tracks → search artist) — the app shows the real count

### Affected artists / patterns
Any artist whose track names contain contractions (`I'm`, `don't`, `you're`,
`it's`, `we're`, etc.) is potentially affected. The issue is inconsistent —
some tracks with apostrophes resolve fine, others don't.

---

## 2. Incomplete album track lists

### What happens
`get_album_info` returns a track list, but it may be truncated. Last.fm's album
entries are community-edited and sometimes only list 10 tracks even when the album
has 14+.

### Mitigation
Always cross-check the track count from `get_album_info` against the known
official track count (from Wikipedia/web search). Fetch missing tracks individually
with `get_track_info`.

---

## 3. Deluxe editions double-counting

### What happens
If you call `get_album_info` on both the standard and Deluxe versions, both will
return a `your plays` total that covers the base tracks. Adding them together
double-counts those tracks.

### Mitigation
- Use the **standard** album total as the authoritative base-track figure
- Fetch the **bonus tracks** individually and add those counts on top
- Discard the Deluxe album total entirely (or note it as "alternative tagging")

---

## 4. get_album_info errors

### What happens
Sometimes `get_album_info` throws: `Cannot read properties of undefined (reading 'slice')`

This typically means the album doesn't exist as a Last.fm album entry yet
(e.g. a future release with no scrobbles yet, or a very obscure album).

### Mitigation
Fall back to fetching all tracks individually with `get_track_info`.

---

## 5. Track name variations

Different music players tag the same track differently. For example:
- `feat.` vs `ft.` vs `(with Artist)`
- `&` vs `and`
- Capitalisation differences

If `get_track_info` returns unexpectedly low plays, try alternate spellings.
