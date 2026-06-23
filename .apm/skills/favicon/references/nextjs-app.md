# Next.js (App Router) — Favicon Reference

## Preferred method: Metadata API (Next.js 13.2+)

Next.js App Router has first-class favicon support via file-based metadata conventions.
**Do not manually add `<link>` tags** — Next.js generates them automatically.

## File placement

Place files directly in `app/`:

```
app/
├── favicon.ico          ← auto-detected, no config needed
├── icon.svg             ← auto-detected as SVG icon
├── apple-icon.png       ← auto-detected as Apple touch icon (must be 180×180)
└── manifest.ts          ← or manifest.json
```

Next.js will automatically inject the correct `<head>` tags for these files.

## `app/manifest.ts` (TypeScript)

```ts
import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'App Name',
    short_name: 'App',
    icons: [
      { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    theme_color: '#ffffff',
    background_color: '#ffffff',
    display: 'standalone',
  }
}
```

## PNG icons not auto-detected

`icon-192.png` and `icon-512.png` are **not** auto-detected. Place them in `public/` and reference them only from the manifest:

```
public/
├── icon-192.png
└── icon-512.png
```

## Fixing an inline `data:` URI

If the project has a `layout.tsx` with a manual `<link rel="icon" href="data:...">`:

1. Remove or replace the manual tag — it overrides Next.js metadata
2. Save the SVG as `app/icon.svg`
3. Delete any manual favicon `<link>` tags from `layout.tsx`

## Notes

- `favicon.ico` in `app/` takes precedence over `public/favicon.ico`
- Next.js serves app-dir metadata files at the root path automatically
- For dynamic icons, use `app/icon.tsx` with `ImageResponse`
