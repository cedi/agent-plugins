---
tags:
  - meta
created: 2026-01-01
aliases:
  - Agent Config
agent_config:
  identity:
    github_login: your-github-login
    jira_cloud_id: yourorg.atlassian.net
    jira_project: PROJ
    slack_workspace_host: your-workspace.enterprise.slack.com
    slack_canonical_host: yourorg.slack.com
  paths:
    repos_root: ~/src
    impact_log_dir: Career/Impact Log
    daily_dir: Daily
    inbox_dir: 00 Inbox
    tasks_index: Tasks.md
    cadence_note: Career/Path/0 - README.md
    career_goals_dir: Career/Path
  conventions:
    cadence_tag: career-tracking
    career_framework: ""
    translate_languages:
      - en
  sources:
    slack: true
    github: true
    jira: true
    datadog: false
    datadog_fallback_pup: false
    google_workspace: false
---

# Agent Config (example)

Copy this into your vault as `Meta/Agent Config.md` and fill in your own values. The
`vault-*` skills read the `agent_config` frontmatter above. See the README for what
each field means. Leave `career_framework` blank to skip promotion-ladder framing,
and set `sources.*` to match the MCPs you actually have.
