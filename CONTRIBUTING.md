# Contributing

## Conventional Commits

Releases and the changelog are automated with
[release-please](https://github.com/googleapis/release-please), which reads
[Conventional Commits](https://www.conventionalcommits.org/). Use these types:

| Type | Changelog section | Version bump |
|------|-------------------|--------------|
| `feat:` | Features | minor |
| `fix:` | Bug Fixes | patch |
| `skill:` | Skills | patch |
| `agent:` | Agents | patch |
| `docs:` | Documentation | patch |
| `refactor:` | Refactoring | patch |
| `chore:` | (hidden) | none |

A `!` suffix or `BREAKING CHANGE:` footer triggers a major bump, e.g.
`feat!: drop the foo skill`.

## Adding content

- **Skill** (works in all four tools): create `skills/<name>/SKILL.md` with
  `name` + `description` frontmatter, then symlink it into a plugin:
  `ln -s ../../../skills/<name> plugins/<plugin>/skills/<name>`.
- **Agent** (Claude Code only): add `plugins/<plugin>/agents/<name>.md`.
- **Output style** (Claude Code only): add `plugins/<plugin>/output-styles/<name>.md`.

If you add a new plugin, list it in `.claude-plugin/marketplace.json` and add its
`plugin.json` version to `release-please-config.json` `extra-files`.

## Validate locally

```
pip install pyyaml
python3 scripts/validate.py
```

CI runs the same validator on every push and pull request.
