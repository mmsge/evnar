# Plain HTML — Favicon Reference

## File placement

All favicon assets go in the **web root** (the directory your server serves from):

```
project/
├── index.html
├── favicon.ico
├── favicon.svg
├── apple-touch-icon.png
├── icon-192.png
├── icon-512.png
└── site.webmanifest
```

## `<head>` snippet

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

## Notes

- Paths use absolute root-relative URLs (`/favicon.svg`) — works regardless of page depth
- No build step needed; files are served as-is
