# jotta-cli notes (the hard-won bits)

Everything here was learned the hard way pulling 31 May 2026 off Jottacloud. Read it
before changing discovery or download logic.

## The listing cap (the big one)

`jotta-cli ls <folder> --json` **silently caps long listings at ~850 entries**, ordered
**oldest-upload-first**. For a busy month, the newest clips simply never appear in the
listing — e.g. the May folder listed dates up to the 30th and stopped, so 31 May was
invisible even though the folder genuinely contained it.

- The cap is applied **before** sorting, so `-t` (sort by modified time) does **not**
  surface the missing entries. Don't rely on it.
- There is no offset/pagination flag to page past the cap.
- `discover --mode auto` detects this: it reads the newest date present in the listing
  and, if the requested date is beyond it (or sits right at the cap edge), it warns or
  refuses and tells you to use album mode.

## Direct-path download ignores the cap

`jotta-cli download "<exact/path>" <dest>` resolves the path directly and works for
files the listing never showed. This is why the whole pipeline downloads by exact
`Path`, never by re-listing. If you know the path, you can always get the file.

## The album bridge

Albums are small, so their listing is **complete** — no cap. And each album entry's
JSON carries the real `Path`, which is the downloadable timeline path. So:

1. On the phone, filter to the day's videos (the app *can* filter by type + date) and
   add them to an album.
2. `jotta-cli ls "/Photos/Albums/<name>" --json` → complete list, with paths.

This is the reliable route for any date that the auto listing can't reach.

**Album sync lag:** a freshly created album shows up in the CLI a little after you make
it. We saw a partial album (11 clips) on first listing and the full 165 a few minutes
later. If an album looks short, wait and re-list.

## Parse JSON, never the grid

The default `ls` grid output mangles when piped (column wrapping / padding), so
`grep`-ing it for filenames fails even though bytes flow. Always use `--json` and read
the `Files[].Name` / `Files[].Path` fields.

## --merge = idempotent

`jotta-cli download ... --merge` checksums files already on disk and skips them. Every
download in this pipeline uses it, so re-running `fetch` only fills gaps and never
re-pulls a 200 MB clip you already have.

## Misc

- The CLI is **case-insensitive** on paths, but quote names with spaces or `æøå`
  (`"/Photos/Albums/Sjælland rundt"`). With `subprocess` list-args, no shell quoting is
  needed — pass the path as one argv element.
- Timeline month folders use **unpadded** months: `/Photos/Timeline/2026/5`, not `/05`.
- JSON `Path` values come back lowercase (`/photos/...`); capital-P paths work too.
- Downloads are **async and queued** — `jotta-cli download` returns immediately and jobs
  run one at a time. `fetch` fires them all, then waits by comparing on-disk file size
  to the manifest `Size` (a file matches its expected size only when complete).
