---
name: vault-weekly-review
description: Use when the user wants a weekly review, a work-log or impact-log update, or a synthesis of recent work written into their Obsidian vault. Triggers include "weekly review", "update my impact log", "what did I do this week", "summarize my week into the vault".
---

# vault-weekly-review

Synthesize recent work into the vault's work/impact log, framed by outcome and
impact rather than activity. The forward-looking counterpart is
`vault-weekly-planning`.

## Prerequisite

Read two things:
- The vault conventions file (root `AGENTS.md` or `CLAUDE.md`) for the log's
  frontmatter schema, tag and inline-date conventions, writing style, and the
  write-zone policy.
- The vault agent config (the `agent_config` frontmatter of `Meta/Agent Config.md`,
  or the path your setup defines) for `paths.impact_log_dir`, `paths.repos_root`,
  `paths.daily_dir`, `paths.inbox_dir`, `identity.slack_workspace_host`,
  `identity.slack_canonical_host`, `conventions.cadence_tag`,
  `conventions.career_framework`, `conventions.translate_languages`, and `sources.*`.
  If the config note is absent, ask the user for the values you need; do not assume.

The log usually sits in a curated ask-first zone, so propose additions and get
approval before writing. Use the obsidian MCP.

## Gather

Pull what happened in the period from every enabled, available source. Skip any
whose MCP is unauthenticated and say so.

- Slack (`sources.slack`), the primary impact source. Recipe:
  1. Resolve the user's own id with `slack_read_user_profile` (no argument).
  2. Set the window: the day after the last dated line in the newest log file under
     `paths.impact_log_dir`, through today. State it.
  3. Confirm the user is OK searching private channels and DMs; the private search
     asks for consent anyway.
  4. Fan out ONE subagent to mine the window and return a compact digest, so the
     noisy raw messages never enter the main context. Tell it to query
     `slack_search_public_and_private` with `from:<@USER_ID> after:START before:END`
     (pad each end by a day), sort timestamp ascending, page the cursor to the end,
     translate any `conventions.translate_languages` into the log's language, and
     return per item only: date, one-line outcome, channel, permalink. Keep shipped
     work, PRs, incidents, cross-team help, decisions, and risks flagged; drop
     greetings, reactions, and logistics.
  OAuth-based MCPs (Slack among them) often cannot authenticate in headless runs; if
  the slack MCP is unauthenticated, say so and continue with the other sources.
- git across the user's repos under `paths.repos_root`: merged commits and PRs
  (`git log --author --since`).
- The vault's daily notes (`paths.daily_dir`) and inbox captures (`paths.inbox_dir`)
  for the period.
- Optional doc sources (e.g. a Google Workspace MCP if `sources.google_workspace`):
  docs the user authored or contributed to in the period; skip if absent.
- Anything the user points you at.

Only include what you can verify. Never invent impact. Attribute each entry to its
source so the user can check it.

## Synthesize

1. Target file: `<paths.impact_log_dir>/YYYY-MM.md` (month granularity). If missing,
   create it with the log frontmatter from the conventions file.
2. Lead each entry with outcome and scope (what changed, who it helped, the
   reliability or business impact), not a task list. If `conventions.career_framework`
   is set (a promotion ladder), tie each entry to the dimension it demonstrates.
3. Timestamp lines with the inline date tag (`#YYYY-MM-DD`) per the log convention.
4. Follow the vault writing style from the conventions file.
5. Wikilink people only when a `People/` note exists; otherwise plain text. Link
   Jira, GitHub, and Slack as markdown links. If `identity.slack_canonical_host` is
   set, normalize Slack permalinks from `identity.slack_workspace_host` to
   `<slack_canonical_host>/archives/<channel>/p<ts>` to match the existing log.

## Reconcile tasks

The mined evidence often shows an open vault task is already done. After Synthesize,
reconcile, conservatively:

1. Collect open tasks (`- [ ]`) from the vault, excluding `Templates/`. The vault's
   task index (`paths.tasks_index`) aggregates them.
2. Propose a completion ONLY when a specific piece of evidence unambiguously maps to
   a specific task, for example a task naming a PR or doc now merged or shipped. No
   fuzzy or thematic matches.
3. Never touch aspirational milestone checklists (under `paths.career_goals_dir`) or
   any recurring `[repeat::]` task. Completing a `[repeat::]` task by file edit does
   not spawn its next occurrence (only the Tasks plugin does), so list due recurring
   `#<conventions.cadence_tag>` tasks separately as a reminder to tick in the app,
   and leave them unchecked.
4. Interactive run: show each candidate as its task text, `file:line`, and the
   evidence link. Tasks live in curated ask-first zones, so mark done only after
   approval, in place, as `- [x] … ✅ YYYY-MM-DD` (append today's date; keep the rest
   of the line and its tags intact).
5. Headless run: list candidates in the draft only. Never edit a task.

## Write (ask first)

The log's zone is curated. Show the proposed entries and the exact target path, then
append after approval. Add to existing entries; never overwrite them.

## Output contract

Log entries appended to the correct month file, each dated, factual, and
impact-framed, approved before writing. No padding, no invented outcomes. Candidate
task completions listed with their evidence, marked done only after approval and
only in an interactive run.
