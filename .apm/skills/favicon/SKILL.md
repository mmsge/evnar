---
name: favicon
description: >
  Set up favicons correctly for any web project — both creating from scratch and fixing
  broken or incomplete existing favicon implementations. Use this skill whenever a user
  mentions favicons, site icons, browser tab icons, PWA icons, Apple touch icons, or
  web manifest icons. Also trigger when a user reports that their favicon isn't showing
  up in Google Search, social media link previews, or browser tabs. Trigger for phrases
  like "add a favicon", "fix my favicon", "favicon not showing", "site icon", "tab icon",
  "create favicon", "favicon from SVG", "emoji favicon", "PWA icons", or "web manifest
  icons". Always use this skill — do NOT improvise a favicon setup without it.
---

# Favicon Skill

Sets up a complete, production-ready favicon implementation. Covers:

- Creating favicons from scratch (SVG source, emoji, or text)
- Fixing broken/incomplete favicon setups (e.g. inline `data:` URIs that Google can't fetch)
- Generating all required formats and sizes
- Injecting correct `<head>` markup
- Framework-specific placement and config

---

## Step 1 — Diagnose or gather intent

**If fixing an existing favicon:**
1. Inspect the current `<head>` — look for `<link rel="icon">` tags
2. Check if `href` is an inline `data:` URI (Google/external services can't fetch these)
3. Check if `/favicon.ico` exists at the root
4. Check if a web manifest (`site.webmanifest` or `manifest.json`) is present and correct
5. Note which formats/sizes are missing

**If creating from scratch, ask:**
1. What is the source? SVG file, emoji, text/initials, or an uploaded image?
2. Does the project need PWA support? (affects manifest + maskable icon)
3. What framework? (affects file placement — see Step 2)

---

## Step 2 — Select the framework reference

Read the appropriate reference file before generating any files:

| Framework / Stack         | Reference file                    |
|---------------------------|-----------------------------------|
| Plain HTML                | `references/plain-html.md`        |
| Next.js (App Router)      | `references/nextjs-app.md`        |
| Next.js (Pages Router)    | `references/nextjs-pages.md`      |
| SvelteKit                 | `references/sveltekit.md`         |
| Astro                     | `references/astro.md`             |
| Vite (React/Vue/vanilla)  | `references/vite.md`              |
| Nuxt                      | `references/nuxt.md`              |

If the stack isn't listed, use `references/plain-html.md` as a baseline and adapt paths accordingly.

---

## Step 3 — Generate the favicon assets

### Required output files (every project)

| File                   | Purpose                                              |
|------------------------|------------------------------------------------------|
| `favicon.svg`          | Primary vector icon — used by modern browsers        |
| `favicon.ico`          | Legacy fallback — IE, old crawlers                   |
| `apple-touch-icon.png` | 180×180 — iOS home screen                           |
| `icon-192.png`         | 192×192 — Android / PWA                             |
| `icon-512.png`         | 512×512 — Android splash / PWA install              |
| `site.webmanifest`     | PWA manifest linking icons                          |

### SVG source → all formats

Use the `sharp` npm package or `cairosvg` + `Pillow` (Python) to rasterise SVG:

```bash
# Node (sharp)
npx sharp-cli --input favicon.svg --output favicon-192.png --width 192 --height 192
npx sharp-cli --input favicon.svg --output favicon-512.png --width 512 --height 512
npx sharp-cli --input favicon.svg --output apple-touch-icon.png --width 180 --height 180

# Python (cairosvg + Pillow)
pip install cairosvg pillow
cairosvg favicon.svg -o favicon-192.png -W 192 -H 192
cairosvg favicon.svg -o favicon-512.png -W 512 -H 512
cairosvg favicon.svg -o apple-touch-icon.png -W 180 -H 180
```

For `.ico` generation (must contain 16×16, 32×32, 48×48):

```python
from PIL import Image
sizes = [(16,16),(32,32),(48,48)]
imgs = [Image.open("favicon.svg").resize(s) for s in sizes]  # use cairosvg first
imgs[0].save("favicon.ico", sizes=sizes)
```

### Emoji or text favicon (SVG)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <text y="1em" font-size="32">🦄</text>
</svg>
```

For text/initials use a monospace or brand font, centred on a coloured background.

### Inline `data:` URI → external file fix

If the existing `<link rel="icon">` uses `href="data:image/svg+xml,..."`:

1. Extract the SVG content from the data URI (URL-decode if needed)
2. Save it as `favicon.svg` in the correct public directory (see framework reference)
3. Replace the `<link>` tag with the external path version

---

## Step 4 — Generate `site.webmanifest`

```json
{
  "name": "App Name",
  "short_name": "App",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

---

## Step 5 — Inject `<head>` markup

The canonical `<head>` snippet (adapt paths per framework reference):

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

**Order matters:** SVG overrides `.ico` for modern browsers; `.ico` is the fallback.  
**Never use an inline `data:` URI** as the sole favicon — external services (Google, Slack, iMessage previews) cannot fetch it.

---

## Step 6 — Verify

After implementation, check:

- [ ] `https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://yourdomain.com&size=64` — shows correct icon (Google's fetch)
- [ ] `https://yourdomain.com/favicon.svg` — returns a valid SVG (not 404)
- [ ] `https://yourdomain.com/favicon.ico` — returns a valid ICO
- [ ] `https://yourdomain.com/site.webmanifest` — returns valid JSON
- [ ] Browser tab shows the correct icon
- [ ] Mobile: "Add to Home Screen" shows the correct icon

Provide these URLs to the user after implementation so they can verify.

---

## Quality checklist

- [ ] No `data:` URI used as the only favicon source
- [ ] `/favicon.ico` exists at the root for legacy support
- [ ] `favicon.svg` is served from the correct public path for the framework
- [ ] All three PNG sizes generated (180, 192, 512)
- [ ] `site.webmanifest` references `/icon-192.png` and `/icon-512.png` with correct paths
- [ ] `<head>` has both `.ico` and `.svg` link tags (SVG last = highest priority)
- [ ] `apple-touch-icon.png` is exactly 180×180
