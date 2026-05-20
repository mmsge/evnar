# APM source tree

This directory is the source of truth for `evnar`.

APM reads primitives from here and deploys generated output to client-specific
directories such as `.claude/`, `.codex/`, `.github/`, `.cursor/`, and the
cross-client `.agents/skills/` directory.

## Layout

```text
.apm/
  skills/<name>/SKILL.md       Agent Skills bundles
  instructions/*.md            Always-on rules for supported clients
  prompts/*.prompt.md          Reusable prompts
  agents/*.agent.md            Named agent definitions
  hooks/                       Lifecycle hooks
  context/                     Shared context fragments
```

MCP servers are declared in the top-level `apm.yml` under
`dependencies.mcp`, because APM wires them through per-client adapters.
