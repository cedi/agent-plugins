# Cedi's Agent Plugins

[![validate](https://github.com/cedi/agent-plugins/actions/workflows/validate.yml/badge.svg)](https://github.com/cedi/agent-plugins/actions/workflows/validate.yml)
[![release](https://img.shields.io/github/v/release/cedi/agent-plugins?logo=github)](https://github.com/cedi/agent-plugins/releases)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-standard-5865F2)](https://agentskills.io)

Reusable AI-agent configuration shared across **Claude Code, OpenCode, Codex, and
Cursor**.

- **Skills** are authored once in the open [Agent Skills](https://agentskills.io)
  standard (a flat `<name>/SKILL.md` dir) and then exposed through generated
  plugin manifests for Claude Code, Codex, and Cursor.
- **Agents** and **output styles** remain Claude Code-only components, bundled
  into the Claude plugin source manifests.

## Contents

| Plugin | Skills | Agents | Output styles |
|--------|--------|--------|---------------|
| **git-workflows** | changelog-generator, pr-review, pull-request, sre-code-reviewer | — | — |
| **documentation** | documentation, strategic-design-doc | design-doc | — |
| **tpm** | jira-cli | — | — |
| **product-design** | cognitive-load, fogg-behavior-mode, trust-psychology | — | — |
| **mental-models** | five-why, graph-thinking, tit-for-tat | — | talk |
| **second-brain** | vault-capture, vault-weekly-review, vault-weekly-planning, vault-curate, vault-ask, vault-link, vault-moc | — | — |

## Install

### Claude Code

```sh
claude plugin marketplace add cedi/agent-plugins
claude plugin install git-workflows@cedi-agent-plugins
```

Installs the skills **and** the bundled agent (`design-doc`) and output style
(`talk`).

### Cursor

Cursor consumes this repo as a plugin marketplace via the generated
`.cursor-plugin/` index. Add the marketplace by repository (`cedi/agent-plugins`)
and install the plugin from Cursor's plugin UI.

### Codex

Codex consumes the generated repo-local marketplace at
`.agents/plugins/marketplace.json` and each plugin's `.codex-plugin/plugin.json`.
Add the repo as a marketplace and install the plugin you want:

```sh
codex plugin marketplace add /path/to/agent-plugins
codex plugin install git-workflows@cedi-agent-plugins
```

### OpenCode

```sh
./install.sh
```

OpenCode still reads flat skills from `~/.agents/skills/`. The installer is
idempotent and additive — existing entries are left untouched.

> [!WARNING]
> If `~/.agents/skills` is a symlink into your dotfiles, the installer refuses to
> write through it. Convert it to a real directory first (a symlink farm
> aggregating any externally-managed skills and this repo).

## Layout

```
skills/<name>/SKILL.md                # canonical skills — source of truth

.claude-plugin/marketplace.json       # canonical marketplace index
.cursor-plugin/marketplace.json       # generated Cursor marketplace
.agents/plugins/marketplace.json      # generated Codex marketplace
plugins/<plugin>/
  .claude-plugin/plugin.json          # canonical plugin manifest
  .cursor-plugin/plugin.json          # generated Cursor plugin manifest
  .codex-plugin/plugin.json           # generated Codex plugin manifest
  skills/<name> -> ../../../skills/<name>   # symlink to canonical (no duplication)
  agents/<name>.md                    # Claude-only subagents
  output-styles/<name>.md             # Claude-only output styles

install.sh                            # wire skills into ~/.agents/skills for OpenCode
scripts/validate.py                   # canonical manifest + frontmatter validator
scripts/sync-vendor-manifests.mjs     # generate Cursor/Codex manifests
```

`plugins/*/skills/*` are symlinks into `skills/`, so each skill exists once.
Within a marketplace install, Claude Code dereferences these symlinks into its
plugin cache, so they work for remote installs too. Cursor and Codex now consume
the same plugin directories through generated manifests instead of reading the
flat skill tree directly.

## How each tool discovers skills

| Tool | Install path |
|------|------|
| Claude Code | Marketplace plugins from `.claude-plugin/` |
| Cursor | Marketplace plugins from generated `.cursor-plugin/` |
| Codex | Marketplace plugins from generated `.agents/plugins/marketplace.json` + `.codex-plugin/` |
| OpenCode | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |

`~/.agents/skills/` remains the shared flat-skill root for OpenCode and any
manual local installs. Skills must stay flat — OpenCode and Claude Code do not
recurse into category subfolders. Agents and output styles are **not** read by
OpenCode/Codex/Cursor; they work only in Claude Code.

## Development

Releases are automated with [release-please](https://github.com/googleapis/release-please)
from [Conventional Commits](https://www.conventionalcommits.org/), which also
bumps the version in the marketplace and every `plugin.json`. CI validates every
push and PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

```sh
python3 scripts/validate.py
npm run check:sync
```

After editing any canonical `.claude-plugin/` file, regenerate the derived
Cursor and Codex manifests:

```sh
npm run sync
```
