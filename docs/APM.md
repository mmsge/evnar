# Agent Package Manager

`evnar` is an APM package. The top-level `apm.yml` declares package metadata,
target clients, dependencies, MCP servers, and scripts. The `.apm/` directory
is the authored source tree.

## Daily use

Install APM from the upstream project, then run:

```bash
apm install --target all,agent-skills
```

or use the wrapper:

```bash
./install.sh
```

The wrapper calls `apm install --target all,agent-skills` when `apm` is on
`PATH`. If APM is not installed, it falls back to the old Claude-only skill
symlink install into `~/.claude/skills`.

## Add local content

- Skills: add a folder under `.apm/skills/<name>/` with `SKILL.md`.
- Instructions: add Markdown files under `.apm/instructions/`.
- Prompts: add files named `*.prompt.md` under `.apm/prompts/`.
- Agents: add files named `*.agent.md` under `.apm/agents/`.
- MCP servers: add entries under `dependencies.mcp` in `apm.yml`.

Generated deployment output is ignored by git. Edit `.apm/` and rerun
`apm install`.

## Useful commands

```bash
apm targets
apm install --target all,agent-skills --dry-run
apm install --target all,agent-skills
apm audit
apm pack
```
