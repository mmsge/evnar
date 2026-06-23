# Vite (React / Vue / vanilla) — Favicon Reference

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

Vite copies `public/` to the build output root unchanged.

## `<head>` snippet

Add to `index.html` (Vite's entry HTML):

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

## React: fixing an inline `data:` URI from Vite's default scaffold

Vite's React template generates:
```html
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
```

Replace with the full icon set above, and replace `vite.svg` with your own `favicon.svg`.

## `vite-plugin-pwa`

If using `vite-plugin-pwa`, configure icons in `vite.config.ts`:

```ts
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      manifest: {
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
})
```

## Notes

- `public/` assets are **not** processed by Vite — they're copied as-is
- Do not import favicon files via JS/TS — reference them by path from `index.html`
