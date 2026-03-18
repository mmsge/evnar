---
name: new-project-scaffold
description: >
  Bootstrap new software projects in blank/empty repositories with a complete, production-ready structure.
  Use this skill whenever a user wants to start a new project, scaffold a repository, bootstrap a codebase,
  set up a new app or library, or initialise a blank GitHub repo. Triggers include phrases like start a new
  project, scaffold a repo, bootstrap a project, set up a new app, initialise a project, create a new repo
  structure, help me start from scratch, blank repo, or new codebase. Always use this skill — do NOT
  improvise a project structure without it.
---

# New Project Scaffold Skill

Bootstraps a complete, production-ready project in a blank repository. Every project gets:

- **Docusaurus-optimised `/docs` folder** with documentation for every core feature
- **Root README** with badges, description, and run instructions
- **Tests** with maximum practical coverage
- **GitHub Actions workflows** for lint, format, and test CI

---

## Step 1 — Gather requirements

Ask (or infer from context) before generating anything:

1. **Project name** — what is it called?
2. **What does it do?** — one-sentence description
3. **Language / framework** — e.g. TypeScript + Node, Python, Rust, Go, React, etc.
4. **Project type** — CLI, library, web app, API, monorepo, etc.
5. **Package manager** — npm/pnpm/yarn, pip/uv/poetry, cargo, go modules, etc.

If the user has given enough context, skip straight to generation without asking.

---

## Step 2 — Select the language reference

Read the appropriate reference file before generating any files:

| Language / Stack | Reference file |
|---|---|
| TypeScript / Node | `references/typescript.md` |
| Python | `references/python.md` |
| Go | `references/go.md` |
| Rust | `references/rust.md` |
| React / Next.js | `references/react.md` |

If the stack isn't listed, use `references/generic.md` as a baseline and adapt.

---

## Step 3 — Generate the scaffold

Create **all files in one pass** using `create_file` or `bash_tool`. Never ask the user to create files themselves.

### Required structure (every project)

```
<project-root>/
├── .github/
│   └── workflows/
│       ├── ci.yml          # lint + format + test on push/PR
│       └── release.yml     # (optional) publish on tag
├── docs/                   # Docusaurus site
│   ├── docusaurus.config.js
│   ├── sidebars.js
│   ├── package.json
│   └── docs/
│       ├── intro.md        # Getting started
│       ├── installation.md
│       ├── configuration.md
│       └── api/            # One .md per core module/function
├── src/                    # (or lib/, app/, cmd/ etc per language)
├── tests/                  # (or __tests__/, spec/, *_test.go etc)
├── .gitignore
├── .eslintrc.* / .ruff.toml / .golangci.yml etc
├── README.md
└── <manifest>              # package.json / pyproject.toml / Cargo.toml / go.mod
```

### README.md requirements

- Badges: CI status, coverage (if available), version/npm/PyPI, licence
- One-paragraph description
- Feature list (bullet)
- **Quick start** — copy-pasteable commands to install and run
- **Development** — how to run tests and linting locally
- Link to `/docs` for full documentation

Badge templates:
```markdown
![CI](https://github.com/<org>/<repo>/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/<org>/<repo>/badge.svg)
![npm](https://img.shields.io/npm/v/<package-name>)
![PyPI](https://img.shields.io/pypi/v/<package-name>)
![License](https://img.shields.io/github/license/<org>/<repo>)
```

### `/docs` Docusaurus requirements

Use **Docusaurus v3**. Every core module or feature must have its own `.md` file under `docs/docs/`. Structure:

```
docs/docs/
├── intro.md          — What the project does, 30-second pitch
├── installation.md   — Install steps for all supported platforms
├── configuration.md  — All config options, with types and defaults
├── api/
│   └── <module>.md   — One file per exported module / major feature
└── contributing.md   — How to run locally, PR process
```

`docusaurus.config.js` must include:
- `title`, `tagline`, `url` (use `https://example.com` as placeholder)
- GitHub Pages `baseUrl`
- Navbar with link to GitHub repo
- Footer with licence

### Tests requirements

- Test **every public function / route / command**
- Aim for **≥ 80% line coverage** (document this target)
- Include at minimum: happy-path, edge cases, error/invalid-input cases
- Use the idiomatic test runner for the language (see reference files)
- Place a coverage config in the manifest or a dedicated config file

### GitHub Actions — `ci.yml`

```yaml
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - # language-specific setup (see reference files)
      - name: Lint
        run: <lint command>
      - name: Format check
        run: <format check command>
      - name: Test
        run: <test command with coverage>
      - name: Upload coverage
        uses: codecov/codecov-action@v4   # optional but recommended
```

---

## Step 4 — Output

After generating all files:

1. Use `present_files` to surface the most important files (README, ci.yml, main source, test file).
2. Give the user a **single code block** with the exact commands to bootstrap and run the project locally.
3. Note any placeholder values they need to fill in (repo URL, org name, package name on registries, etc.).

---

## Quality checklist (run mentally before presenting)

- [ ] README has CI badge pointing to the correct workflow file name
- [ ] `docs/` folder is self-contained (`cd docs && npm install && npm start` works)
- [ ] Every exported function/class/command has a corresponding test
- [ ] Every exported function/class/command has a corresponding `/docs/docs/api/` page
- [ ] `.gitignore` covers language-specific build artefacts, node_modules, .env files
- [ ] CI workflow uses pinned action versions (`@v4` etc.)
- [ ] No secrets or real credentials appear anywhere in generated files
