# React / Next.js Reference

## Toolchain

| Concern | Tool |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript 5 |
| Package manager | pnpm |
| Linter | ESLint + `eslint-config-next` |
| Formatter | Prettier |
| Component tests | Vitest + React Testing Library |
| E2E tests | Playwright (optional, add if requested) |
| Coverage | Vitest built-in (v8) |

---

## Bootstrap command

```bash
pnpm create next-app@latest <project-name> \
  --typescript --eslint --tailwind --app --src-dir --import-alias "@/*"
```

After bootstrapping, add testing tools:

```bash
pnpm add -D vitest @vitest/coverage-v8 @testing-library/react \
  @testing-library/jest-dom @testing-library/user-event \
  @vitejs/plugin-react jsdom
```

## `vitest.config.ts`

```ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: ['node_modules', '.next', 'src/test'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 70,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

## `src/test/setup.ts`

```ts
import '@testing-library/jest-dom';
```

## Test file pattern

```tsx
// src/components/__tests__/MyComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders the label', () => {
    render(<MyComponent label="Click me" onClick={vi.fn()} />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when button is pressed', async () => {
    const handleClick = vi.fn();
    render(<MyComponent label="Go" onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it('disables button when disabled prop is true', () => {
    render(<MyComponent label="Go" onClick={vi.fn()} disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

## `package.json` scripts additions

Add to the Next.js default scripts:

```json
{
  "scripts": {
    "test": "vitest run --coverage",
    "test:watch": "vitest",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

## GitHub Actions — CI

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v3
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Format check
        run: pnpm format:check

      - name: Type check
        run: pnpm tsc --noEmit

      - name: Test
        run: pnpm test

      - name: Build
        run: pnpm build

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage/lcov.info
```

## `.gitignore`

```
# Next.js
.next/
out/
build/

node_modules/
coverage/
.env
.env.local
.env*.local

# Vercel
.vercel

*.tsbuildinfo
next-env.d.ts
```
