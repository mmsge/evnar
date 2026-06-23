# TypeScript / Node.js Reference

## Toolchain

| Concern | Tool |
|---|---|
| Runtime | Node.js ≥ 20 |
| Language | TypeScript 5 |
| Package manager | pnpm (preferred) or npm |
| Linter | ESLint + `@typescript-eslint` |
| Formatter | Prettier |
| Test runner | Vitest |
| Coverage | Vitest built-in (v8) |
| Build | `tsc` or `tsup` (for libraries) |

---

## `package.json` template

```json
{
  "name": "<project-name>",
  "version": "0.1.0",
  "description": "<description>",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsx watch src/index.ts",
    "lint": "eslint src tests --ext .ts",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "vitest run --coverage",
    "test:watch": "vitest"
  },
  "devDependencies": {
    "@typescript-eslint/eslint-plugin": "^7.0.0",
    "@typescript-eslint/parser": "^7.0.0",
    "@vitest/coverage-v8": "^1.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "tsup": "^8.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## `.eslintrc.json`

```json
{
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

## `.prettierrc`

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100
}
```

## `vitest.config.ts`

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 70,
      },
    },
  },
});
```

## Test file pattern

```ts
// tests/example.test.ts
import { describe, it, expect } from 'vitest';
import { myFunction } from '../src/example.js';

describe('myFunction', () => {
  it('returns expected value for valid input', () => {
    expect(myFunction('hello')).toBe('HELLO');
  });

  it('throws on null input', () => {
    expect(() => myFunction(null as any)).toThrow('Input must be a string');
  });

  it('handles empty string', () => {
    expect(myFunction('')).toBe('');
  });
});
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

      - name: Test
        run: pnpm test

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage/lcov.info
```

## `.gitignore`

```
node_modules/
dist/
coverage/
.env
.env.local
*.tsbuildinfo
```
