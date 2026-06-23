# SvelteKit — Favicon Reference

## File placement

All static assets go in `static/`:

```
static/
├── favicon.ico
├── favicon.svg
├── apple-touch-icon.png
├── icon-192.png
├── icon-512.png
└── site.webmanifest
```

SvelteKit serves `static/` at the root path.

## `<head>` snippet

Add to `src/app.html`:

```html
<link rel="icon" href="%sveltekit.assets%/favicon.ico" sizes="32x32">
<link rel="icon" href="%sveltekit.assets%/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="%sveltekit.assets%/apple-touch-icon.png">
<link rel="manifest" href="%sveltekit.assets%/site.webmanifest">
```

`%sveltekit.assets%` resolves to the correct base path (important for non-root deployments).

## Default scaffold

SvelteKit creates `static/favicon.png` by default — replace it with `favicon.ico` + `favicon.svg` + the full icon set.

## Fixing an inline `data:` URI

If a `+layout.svelte` has a `<svelte:head>` block with `data:` URI:

1. Extract and save SVG to `static/favicon.svg`
2. Replace the `<svelte:head>` link with `%sveltekit.assets%/favicon.svg`
3. Or move all `<link>` tags to `src/app.html` (preferred — avoids hydration flash)

## Notes

- Avoid putting favicon links in `+layout.svelte` if possible — `app.html` renders before JS and avoids a flash of the default icon
- `%sveltekit.assets%` is the correct way to reference static assets in `app.html`
