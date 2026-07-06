---
document_type: process
tags:
  - meta
  - 2026-07-06
created: 2026-07-06
aliases:
  - Weekly Vault Review automation
  - weekly review prompt
---

# Weekly Vault Review (headless job)

The `weekly-vault-review` scheduler runs `~/.claude/scripts/weekly-vault-review.sh`,
which feeds the prompt below to a headless `claude` and drafts the result into the
vault's inbox. The runner reads the vault path and this prompt's location from
`OBS_VAULT` and an optional runner env file (see the script header). This note and
[[Agent Config]] both live under `Meta/`.

Only the first fenced code block is the prompt. Edit inside the block to change what
the job does; everything outside it is commentary the job ignores. Do not add
another fenced block above it, and keep the "draft to inbox, never curated" rule
unless you want the job to write curated notes unattended.

```text
Follow the vault-weekly-review skill for the last 7 days. Read the vault agent
config (Meta/Agent Config.md) and the vault conventions file first, then use every
source reachable from this headless CLI context: local git under the config's
repos_root, the vault's daily and inbox notes, and any source MCP that is
authenticated here (skip the rest silently; OAuth MCPs such as Slack are usually not
available headless).

Override the skill's Write step: do NOT write to any curated zone. Save the result
as a DRAFT to `<inbox_dir>/<YYYY-MM-DD> weekly review (draft).md` (inbox_dir from the
config), using the vault's frontmatter and writing style. If the obsidian MCP is
unreachable, write the same file directly to the filesystem under the vault's inbox.

Also reconcile tasks read-only: in a section titled "Candidate task completions",
list only open tasks the gathered evidence directly proves done (a named PR merged,
a doc shipped), each with its file:line and evidence link, and separately list any
due recurring cadence tasks as reminders. Do NOT edit or complete any task.

Finish by printing the exact path you wrote.
```
