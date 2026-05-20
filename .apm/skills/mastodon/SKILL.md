---
name: mastodon
description: Fetch and display Markus's latest Mastodon posts from @markus@skvip.lol. Use this skill whenever Markus asks about his Mastodon posts, toots, activity, what he has posted recently, his fediverse posts, or anything related to his Mastodon account. Always use this skill — do NOT try to web search or guess post content.
---

# Mastodon Skill

Fetches Markus's latest posts from his Mastodon account at @markus@skvip.lol via the Mastodon API.

## Configuration

- **Instance**: `skvip.lol`
- **Account**: `@markus`
- **Default limit**: 5 posts
- **API token**: stored in Google Drive document titled "Claude – Mastodon API Token"

## How to fetch posts

### Step 1: Get the API token

Read the token from the bundled reference file: `references/token.md`.

### Step 2: Get account ID

```
GET https://skvip.lol/api/v1/accounts/lookup?acct=markus
Authorization: Bearer <token>
```

Extract the `id` field from the response.

### Step 3: Fetch statuses

```
GET https://skvip.lol/api/v1/accounts/<id>/statuses?limit=5&exclude_reblogs=false
Authorization: Bearer <token>
```

### Step 4: Display posts

For each post, show:
- Date and time (format: `DD. MMM YYYY, HH:MM`)
- Content (strip HTML tags)
- Boosts and favourites count if > 0
- Mark boosts (reblogs) clearly as "🔁 Boost: ..."

## Notes

- Strip all HTML tags from `content` field before displaying
- Use Norwegian formatting for dates
- If the token is missing or invalid, tell the user and ask them to provide a new one
