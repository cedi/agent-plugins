# second-brain

Obsidian second-brain workflows for Claude Code: capture, weekly review, weekly
planning, and vault curation. The skills are vault-agnostic. Per-user specifics
(identities, paths, source toggles) live in a config note inside your vault, so the
skills themselves carry nothing personal.

## Skills

- `vault-capture` — file one raw input into a well-linked, correctly-filed note.
- `vault-weekly-review` — synthesize recent work into a work/impact log (backward).
- `vault-weekly-planning` — pull live commitments and deadlines and prioritize the
  week (forward, interactive).
- `vault-curate` — vault health report: orphans, dead links, frontmatter, tags.

## Setup

1. An Obsidian vault with a root conventions file (`AGENTS.md` or `CLAUDE.md`) that
   defines your folder taxonomy, per-type frontmatter schemas, tag scheme, writing
   style, and write-zone policy (auto-write vs ask-first vs read-only zones). The
   skills defer to this file for all of that.
2. An obsidian MCP (for example the Local REST API MCP) so writes flow through
   Obsidian.
3. Copy `examples/Agent Config.example.md` into your vault as `Meta/Agent Config.md`
   and fill in your values.
4. Optional per-source MCPs, matched by the `sources` toggles: Slack, GitHub,
   Atlassian (Jira/Confluence), Datadog.

## Config schema (`agent_config` frontmatter)

- `identity`: `github_login`, `jira_cloud_id`, `jira_project`,
  `slack_workspace_host`, `slack_canonical_host` (Slack permalinks are normalized to
  the canonical host).
- `paths`: `repos_root` (local git checkout root for commit/PR mining),
  `impact_log_dir`, `daily_dir`, `inbox_dir`, `tasks_index`, `cadence_note`,
  `career_goals_dir` (all vault-relative except `repos_root`).
- `conventions`: `cadence_tag` (recurring task tag, no leading #), `career_framework`
  (promotion-ladder label, or blank to skip that framing), `translate_languages`.
- `sources`: booleans for `slack`, `github`, `jira`, `datadog`,
  `datadog_fallback_pup`, and `google_workspace`.

## Headless runner (optional)

`scripts/weekly-vault-review.sh` runs `vault-weekly-review` unattended and drafts a
review into your inbox, never a curated zone. Store the prompt as a note in your
vault (see `examples/Weekly Vault Review.example.md`; its first fenced block is the
prompt). Configure the runner with `OBS_VAULT` (and optionally `CLAUDE_BIN`,
`REVIEW_PROMPT_NOTE`) via the environment or a machine-local
`~/.config/vault-skills/runner.env`, then schedule it with cron, launchd, or systemd.

## Notes

- The Slack source uses an OAuth MCP that usually cannot authenticate in
  headless/cron runs; run the Slack-backed pass interactively. A headless run
  degrades gracefully to git and vault sources.
- The skills never write curated zones without approval, and never complete
  recurring `[repeat::]` tasks by file edit (that breaks the Tasks plugin's next
  occurrence).
- `vault-weekly-planning`'s Datadog on-call step can fall back to a `pup` CLI helper
  if `sources.datadog_fallback_pup` is set; that helper is optional and org-specific.
