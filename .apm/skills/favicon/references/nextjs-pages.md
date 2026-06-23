# Next.js (Pages Router) — Favicon Reference

## File placement

All static favicon assets go in `public/`:

```
public/
├── favicon.ico
├── favicon.svg
├── apple-touch-icon.png
├── icon-192.png
├── icon-512.png
└── site.webmanifest
```

## `<head>` snippet

Add to `pages/_document.tsx` (or `_app.tsx` via `<Head>`):

```tsx
import Head from 'next/head'

// In _document.tsx <Head> or _app.tsx:
<Head>
  <link rel="icon" href="/favicon.ico" sizes="32x32" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
</Head>
```

## Fixing an inline `data:` URI

1. Extract the SVG from the `data:` href
2. Save as `public/favicon.svg`
3. Replace the `<link>` tag with `/favicon.svg`

## Notes

- `public/` maps to `/` at runtime — `public/favicon.svg` is served as `/favicon.svg`
- Pages Router does not auto-detect favicon files; manual `<Head>` tags are required
