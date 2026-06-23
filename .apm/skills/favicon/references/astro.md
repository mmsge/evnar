# Astro — Favicon Reference

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

Add to the base layout component (e.g. `src/layouts/BaseLayout.astro`):

```astro
<link rel="icon" href="/favicon.ico" sizes="32x32" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
```

## Astro's default scaffold

Astro projects ship with `public/favicon.svg` by default — extend it with `.ico` + PNG sizes rather than replacing.

## PWA with `@astrojs/manifest`

If using `@astrojs/manifest` or `astro-pwa`, configure icons in `astro.config.mjs`:

```js
import { defineConfig } from 'astro/config'
import pwa from '@vite-pwa/astro'

export default defineConfig({
  integrations: [
    pwa({
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

- `public/` maps to `/` — `public/favicon.svg` is served as `/favicon.svg`
- Astro does not auto-inject favicon tags; they must be explicit in the layout
