# Nuxt — Favicon Reference

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

## Method 1: `nuxt.config.ts` (preferred)

```ts
export default defineNuxtConfig({
  app: {
    head: {
      link: [
        { rel: 'icon', href: '/favicon.ico', sizes: '32x32' },
        { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
      ],
    },
  },
})
```

## Method 2: `app.vue` via `useHead`

```vue
<script setup>
useHead({
  link: [
    { rel: 'icon', href: '/favicon.ico', sizes: '32x32' },
    { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' },
    { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
    { rel: 'manifest', href: '/site.webmanifest' },
  ],
})
</script>
```

## `@vite-pwa/nuxt`

```ts
export default defineNuxtConfig({
  modules: ['@vite-pwa/nuxt'],
  pwa: {
    manifest: {
      icons: [
        { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
      ],
    },
  },
})
```

## Notes

- Nuxt auto-detects `public/favicon.ico` and adds a default `<link>` — explicit config overrides this
- Prefer `nuxt.config.ts` over per-component `useHead` to ensure consistent head across all routes
