---
name: vault-weekly-planning
description: Use when the user wants to plan or prioritize their week, decide what to focus on, or gather what they have committed to and what is due. Triggers include "plan my week", "weekly planning", "what should I focus on", "prioritize my week", "what did I commit to". Runs interactively and needs live MCP auth (Slack, GitHub, Jira, optionally Datadog).
---

# vault-weekly-planning

Forward-looking weekly planning aid. Pulls the live, open state from where the work
actually lives, surfaces what the user committed to and what is due, and helps
decide the week's focus. The backward-looking counterpart that feeds the work log is
`vault-weekly-review`.

Interactive only. It depends on authenticated MCPs (notably Slack, whose OAuth MCP
usually cannot authenticate in headless/cron runs), so run it from a live session.

## Prerequisite

Read the vault conventions file (root `AGENTS.md` or `CLAUDE.md`) for note
conventions and writing style, and the vault agent config (`agent_config`
frontmatter of `Meta/Agent Config.md`, or your configured path) for
`identity.github_login`, `identity.jira_cloud_id`, `identity.jira_project`,
`paths.daily_dir`, `paths.tasks_index`, `paths.cadence_note`,
`paths.career_goals_dir`, `conventions.cadence_tag`, `conventions.career_framework`,
and `sources.*`. If the config is absent, ask for the values you need; do not
assume. Resolve the Slack user id live with `slack_read_user_profile` (no argument).
Use the obsidian MCP, or the filesystem when the cwd is the vault.

## Gather (live)

Pull the current open state from each enabled source (`sources.*`). Skip any whose
MCP is unauthenticated, say so, and continue. Attribute every item to a source link.

- Slack commitments (primary; `sources.slack`). Fan out ONE subagent so the noisy
  raw messages stay out of the main context. Tell it to search the user's own recent
  messages (last ~2 weeks) with `slack_search_public_and_private` for promise
  language ("I'll", "I will", "let me", "I'll send", "get back", "follow up", "by
  <day>", "next week", "action item", "TODO"), plus threads and DMs where someone is
  awaiting the user's reply or asked a direct question left unanswered. Return per
  item: the commitment, to whom, by when if stated, and the permalink.
- GitHub (`sources.github`, login `identity.github_login`): open PRs the user
  authored (flag stale or ready-to-merge), PRs with review requested from the user,
  assigned issues, and failing checks.
- Jira (`sources.jira`, Atlassian MCP, cloud id `identity.jira_cloud_id`):
  `assignee = currentUser() AND statusCategory != Done`, current-sprint items in
  project `identity.jira_project`, and anything due this week.
- On-call and incidents (`sources.datadog`, Datadog MCP): whether the user is on
  call this period and any open incidents that will claim time. If the MCP is down
  and `sources.datadog_fallback_pup` is set, fall back to the `pup` CLI (use the
  `dd-pup` skill) instead of skipping.
- Docs awaiting the user (if a Confluence or service-catalog MCP is configured):
  pages needing the user's input, review, or authorship.
- Vault: overdue and due recurring `#<conventions.cadence_tag>` tasks in
  `paths.cadence_note`, open `paths.tasks_index` items, the last ~2 weeks of
  `paths.daily_dir` notes for carry-over and meeting follow-ups, and active project
  plus `paths.career_goals_dir` goals (framed by `conventions.career_framework` if
  set) for alignment.

Only include what you can verify. Never invent a commitment.

## Reconcile stale-open items

Before prioritizing, cross-check the open items above against shipped evidence and
flag any that are actually done but not yet updated, so they do not pollute the plan:

- Jira issues in a non-Done status whose referenced PR is merged or whose work
  clearly shipped.
- Open `- [ ]` vault tasks that map unambiguously to a merged PR or shipped doc.
- GitHub issues still open after their closing PR merged.
- Slack commitments already fulfilled (the promised thing shipped per GitHub/Jira).

List each with its link or `file:line` and the evidence, separate from the plan.
Only close a Jira issue, tick a task, or edit anything after explicit approval:
transitions and curated-zone edits are mutations, so never flip silently, and never
complete a recurring `[repeat::]` task by file edit (only the Tasks plugin spawns
the next occurrence).

## Prioritize

Group everything into four buckets:

1. Commitments: things the user told someone they would do. Highest accountability.
2. Deadlines this week: due dates, cadence tasks, on-call, meeting prep.
3. Unblocking others: review requests, questions and threads awaiting the user.
   Weight by reciprocity (the tit-for-tat lens): favor unblocking the people who
   reliably unblock you.
4. High-leverage: the work that unblocks or amplifies the most downstream. Find the
   leverage point rather than the loudest item (the graph-thinking lens: centrality,
   bottlenecks, second-order effects), aligned to current projects and, if set, the
   `conventions.career_framework` dimensions.

Then recommend a focused top 3 to 5 for the week and a short carry-over/watch list.
Call out conflicts honestly (an on-call week stacked with commitments, or more due
than fits).

## Present, then write (interactive)

This is a planning conversation, not a dump. Present the buckets and the recommended
focus, let the user re-rank and cut, then write the agreed plan into today's daily
note (`<paths.daily_dir>/<today>.md`) under its planning section, one subsection per
project to match the note's structure, with commitments and deadlines surfaced.
Follow the vault's write-zone policy for the daily note (usually auto-write); still
show the plan before writing. Do not create or complete tasks unless asked.

## Output contract

A prioritized weekly plan written into today's daily note's planning section, per
project, with a top 3 to 5 focus and a carry-over list. Every item traceable to its
source link. No invented commitments; unauthenticated or disabled sources named as
skipped. Stale-open items that are actually done are listed separately for closure
and updated only after approval.
