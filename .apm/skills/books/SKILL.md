---
name: books
description: >
  Query Markus's personal reading history across StoryGraph and Bookwyrm.
  Use this skill whenever Markus asks about books he has read, when he read something,
  his reading history, reading stats, or anything about his personal library.
  Triggers include: "have I read", "when did I read", "what did I read in [year]",
  "books I've read", "my reading history", "show me my books", "did I finish",
  "find a book I read", "how many books", "my StoryGraph", "my Bookwyrm".
  Always use this skill for personal reading queries — do NOT rely on general knowledge.
---

# Books Skill

This skill lets Markus query his personal reading history from StoryGraph and Bookwyrm.

## Markus's Accounts

| Platform    | Username / Instance                                                |
|-------------|-------------------------------------------------------------------|
| StoryGraph  | `mvrkws` → `https://app.thestorygraph.com/books-read/mvrkws`      |
| Bookwyrm    | `mvrkws` @ `bookwyrm.social` → `https://bookwyrm.social/user/mvrkws/books/read` |

These are hardcoded — no need to ask Markus for them.

---

## Data Sources and How to Access Them

### 1. Bookwyrm (live fetch — preferred for recency)

Bookwyrm exposes public ActivityPub / HTML shelves for public profiles.

**Fetch the "read" shelf:**
```
https://{instance}/user/{username}/books/read
```
Example: `https://bookwyrm.social/user/markus/books/read`

Use `web_fetch` on that URL. The page renders book titles, authors, and finish dates in HTML.

**Paginate** if the response contains a "next page" link — fetch subsequent pages until all books are retrieved.

**Outbox (for activity feed):**
```
https://{instance}/user/{username}/outbox?page=true
```
This returns ActivityPub JSON with `Arrive` / `Update` activities that include `startedReading` and `finishedReading` dates. Fetch with `Accept: application/activity+json` if possible, otherwise parse the HTML shelf page.

**RSS feed** (limited to ~10 most recent items):
```
https://{instance}/user/{username}/rss
```

### 2. StoryGraph (CSV export — comprehensive history)

StoryGraph has no public API. Markus must export his data manually and share the file.

**How to export:**
1. Go to `https://app.thestorygraph.com/manage-account`
2. Scroll to **"Manage Your Data"**
3. Click **"Export StoryGraph Library"**
4. Upload the downloaded CSV to this conversation

**CSV columns to use:**
- `Title` — book title
- `Authors` — author(s)
- `Read Status` — `read`, `currently-reading`, `to-read`, `did-not-finish`
- `Date Read` — finish date (YYYY/MM/DD or MM/DD/YY)
- `Date Added` — when the book was added
- `Star Rating` — 0–5 stars
- `Tags / Bookshelves` — custom tags

---

## Workflow

### Step 1 — Determine what data is available

Always try **both** sources:
1. **Bookwyrm** — fetch live (always attempt this first)
2. **StoryGraph CSV** — use if Markus has uploaded one to the conversation; otherwise guide him to export it

If only doing a quick lookup and no CSV is present, Bookwyrm alone is sufficient. For comprehensive history, ask Markus to upload his StoryGraph CSV export.

### Step 2 — Fetch / parse the data

**Bookwyrm (always try first):**
- Fetch `https://bookwyrm.social/user/mvrkws/books/read`
- Parse book titles, authors, and dates from the HTML
- Paginate: try `?page=2`, `?page=3`, etc. until no more results

**StoryGraph public profile (try before asking for CSV):**
- Fetch `https://app.thestorygraph.com/books-read/mvrkws`
- This works if Markus's profile is set to public

**StoryGraph CSV (most comprehensive):**
- Check if a CSV file has been uploaded to `/mnt/user-data/uploads/`
- If not present and full history is needed, prompt:
  > "For your full StoryGraph history, go to [Manage Account](https://app.thestorygraph.com/manage-account) → Manage Your Data → Export StoryGraph Library, then upload the CSV here."

### Step 3 — Answer the query

Common query types:

| Query type | How to answer |
|---|---|
| "Have I read [book]?" | Search by title (fuzzy match). Report yes/no, plus date if available. |
| "When did I read [book]?" | Return `Date Read` from CSV or finish date from Bookwyrm. |
| "What did I read in [year]?" | Filter by year in `Date Read`. List title + author + date. |
| "How many books did I read in [year]?" | Count filtered results. |
| "Books by [author] I've read" | Filter by author. |
| "What was I reading around [date]?" | Find books with `Date Read` closest to that date. |
| "Show all my read books" | List everything, grouped by year descending. |

### Step 4 — Format the response

- For small results (≤10): list as `**Title** by Author (finished: date)`
- For larger results: group by year, show count per year first
- Always note which source the data came from (StoryGraph CSV / Bookwyrm)
- If date is missing, say "date unknown"

---

## Handling Missing Data

- **No Bookwyrm access** (private profile or unknown username): prompt Markus to share his username/instance or use StoryGraph CSV instead.
- **No StoryGraph CSV**: guide Markus through the export process (see above).
- **Date missing on StoryGraph**: The `Date Read` column is sometimes empty for older Goodreads imports. Fall back to `Date Added` and note the uncertainty.
- **Duplicate entries**: If the same book appears in both sources, merge them and prefer the source with a date.

---

## Tips

- StoryGraph URLs for public profiles also expose a read shelf at:
  `https://app.thestorygraph.com/books-read/USERNAME`
  Try fetching this with `web_fetch` — it may work for public profiles without needing a CSV.
- Bookwyrm shelf pages are paginated with `?page=2`, `?page=3`, etc.
- When searching titles, use fuzzy matching — ignore subtitles, articles ("The", "A"), and minor spelling differences.
