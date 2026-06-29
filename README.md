# Cedi's Agent Plugins

[![validate](https://github.com/cedi/agent-plugins/actions/workflows/validate.yml/badge.svg)](https://github.com/cedi/agent-plugins/actions/workflows/validate.yml)
[![release](https://img.shields.io/github/v/release/cedi/agent-plugins?logo=github)](https://github.com/cedi/agent-plugins/releases)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-standard-5865F2)](https://agentskills.io)

Reusable AI-agent configuration shared across **Claude Code, OpenCode, Codex, and
Cursor**.

- **Skills** are authored once in the open [Agent Skills](https://agentskills.io)
  standard (a flat `<name>/SKILL.md` dir) and consumed by all four tools.
- **Agents** and **output styles** are Claude Code-only components, bundled into
  the plugins so Claude picks them up via the marketplace.

## Contents

| Plugin | Skills | Agents | Output styles |
|--------|--------|--------|---------------|
| **git-workflows** | changelog-generator, pr-review, pull-request, sre-code-reviewer | — | — |
| **documentation** | documentation, strategic-design-doc | design-doc | — |
| **tpm** | jira-cli | — | — |
| **product-design** | cognitive-load, fogg-behavior-mode, trust-psychology | — | — |
| **mental-models** | five-why, graph-thinking, tit-for-tat | — | talk |

## Install

### Claude Code

```sh
claude plugin marketplace add cedi/agent-plugins
claude plugin install git-workflows@cedi-agent-plugins
```

Installs the skills **and** the bundled agent (`design-doc`) and output style
(`talk`).

### OpenCode / Codex / Cursor

```sh
./install.sh
```

Per-skill symlinks the skills into `~/.agents/skills/`, the one global root all
three read. Idempotent and additive — existing entries are left untouched.

> [!WARNING]
> If `~/.agents/skills` is a symlink into your dotfiles, the installer refuses to
> write through it. Convert it to a real directory first (a symlink farm
> aggregating any externally-managed skills and this repo).

## Layout

```
skills/<name>/SKILL.md                # canonical skills — source of truth (all tools)

.claude-plugin/marketplace.json       # Claude Code marketplace manifest
plugins/<plugin>/
  .claude-plugin/plugin.json          # Claude Code plugin manifest
  skills/<name> -> ../../../skills/<name>   # symlink to canonical (no duplication)
  agents/<name>.md                    # Claude-only subagents
  output-styles/<name>.md             # Claude-only output styles

install.sh                            # wire skills into ~/.agents/skills
scripts/validate.py                   # manifest + frontmatter + symlink validator
```

`plugins/*/skills/*` are symlinks into `skills/`, so each skill exists once.
Within a marketplace install, Claude Code dereferences these symlinks into its
plugin cache, so they work for remote installs too.

## How each tool discovers skills

| Tool | Global skill roots it scans |
|------|------|
| Claude Code | `~/.claude/skills/`, or installed marketplace plugins |
| OpenCode | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |
| Codex | `~/.agents/skills/` (follows symlinks) |
| Cursor | `~/.agents/skills/`, `~/.cursor/skills/`, `~/.claude/skills/`, `~/.codex/skills/` |

`~/.agents/skills/` is the one root Codex, OpenCode, and Cursor all read. Skills
must stay flat — OpenCode and Claude Code do not recurse into category subfolders.
Agents and output styles are **not** read by OpenCode/Codex/Cursor; they work only
in Claude Code.

## Development

Releases are automated with [release-please](https://github.com/googleapis/release-please)
from [Conventional Commits](https://www.conventionalcommits.org/), which also
bumps the version in the marketplace and every `plugin.json`. CI validates every
push and PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

```sh
pip install pyyaml && python3 scripts/validate.py
```
