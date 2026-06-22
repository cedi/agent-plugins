# Cedi's Agent Plugins

Reusable AI-agent configuration shared across **Claude Code, OpenCode, Codex, and
Cursor**.

- **Skills** are authored once in the open [Agent Skills](https://agentskills.io)
  standard (a flat `<name>/SKILL.md` dir) and consumed by all four tools.
- **Agents** and **output styles** are Claude Code-only components, bundled into
  the plugins so Claude picks them up via the marketplace.

## Layout

```
skills/<name>/SKILL.md                # canonical skills — source of truth (all tools)

.claude-plugin/marketplace.json       # Claude Code marketplace manifest
plugins/<plugin>/
  .claude-plugin/plugin.json          # Claude Code plugin manifest
  skills/<name> -> ../../../skills/<name>   # symlink to canonical (no duplication)
  agents/<name>.md                    # Claude-only subagents
  output-styles/<name>.md             # Claude-only output styles

install.sh                            # wire skills into ~/.agents/skills (Codex/OpenCode/Cursor)
```

`plugins/*/skills/*` are symlinks into `skills/`, so each skill exists once.
Agents and output styles are real files (Claude-only, single home).

## Contents

| Plugin | Skills | Agents | Output styles |
|--------|--------|--------|---------------|
| **git-workflows** | changelog-generator, pr-review, pull-request | code-reviewer | — |
| **documentation** | documentation, strategic-design-doc | design-doc | — |
| **tpm** | jira-cli | — | — |
| **product-design** | cognitive-load, fogg-behavior-mode, trust-psychology | — | — |
| **mental-models** | five-why, graph-thinking, tit-for-tat | — | talk |

The `plugins/` grouping is a Claude Code packaging concern. OpenCode, Codex, and
Cursor read the flat `skills/` dir and ignore the grouping. They do **not** read
the `agents/` or `output-styles/` dirs — those work only in Claude Code.

## How each tool discovers skills

| Tool | Global skill roots it scans |
|------|------|
| Claude Code | `~/.claude/skills/`, or installed marketplace plugins |
| OpenCode | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |
| Codex | `~/.agents/skills/` (follows symlinks) |
| Cursor | `~/.agents/skills/`, `~/.cursor/skills/`, `~/.claude/skills/`, `~/.codex/skills/` |

`~/.agents/skills/` is the one root Codex, OpenCode, and Cursor all read, so a
single symlink farm there covers all three. (Skills must stay flat — OpenCode and
Claude Code do not recurse into category subfolders.)

## Install

### Claude Code

```
claude plugin marketplace add ~/src/gh/cedi/agent-plugins   # or: cedi/agent-plugins once pushed
claude plugin install git-workflows@cedi-agent-plugins
```

This gives Claude the skills **and** the bundled agents (`code-reviewer`,
`design-doc`) and output style (`talk`).

### Codex / OpenCode / Cursor

```
./install.sh
```

Per-skill symlinks the 12 skills into `~/.agents/skills/`, which all three read.
Idempotent and additive — existing entries (incl. pup-managed `dd-*`) are left
untouched.

> If `~/.agents/skills` is still a symlink into your dotfiles, the installer
> refuses to write through it. Convert it to a real directory first (a symlink
> farm aggregating your `dd-*` skills and this repo).

## Adding things

- **Skill** (cross-tool): create `skills/<name>/SKILL.md`, then symlink it into a
  plugin: `ln -s ../../../skills/<name> plugins/<plugin>/skills/<name>`. Re-run
  `./install.sh`.
- **Agent** (Claude only): drop `plugins/<plugin>/agents/<name>.md` with
  `name` + `description` frontmatter. Auto-discovered.
- **Output style** (Claude only): drop `plugins/<plugin>/output-styles/<name>.md`.
  Auto-discovered.
