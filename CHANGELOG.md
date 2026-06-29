# Changelog

All notable changes to this project are documented here. This file is maintained
automatically by [release-please](https://github.com/googleapis/release-please)
from [Conventional Commits](https://www.conventionalcommits.org/).

## [2.0.0](https://github.com/cedi/agent-plugins/compare/v1.0.0...v2.0.0) (2026-06-29)


### ⚠ BREAKING CHANGES

* the `code-reviewer` agent no longer exists; use the `sre-code-reviewer` skill instead.

### Features

* migrate code-reviewer agent to cross-tool sre-code-reviewer skill ([22dbcf0](https://github.com/cedi/agent-plugins/commit/22dbcf006038b7e7ccded57da2b7bd3dfa1e27f7))


### Documentation

* use GitHub-flavored callout for the ~/.agents warning ([2560efb](https://github.com/cedi/agent-plugins/commit/2560efbf82012167ead4cc92a344a73a60d7eb02))

## 1.0.0 (2026-06-22)

### Features

* Cross-tool agent skills shared across Claude Code, OpenCode, Codex, and Cursor,
  authored in the open [Agent Skills](https://agentskills.io) standard.
* Claude Code plugin marketplace with five plugins: `git-workflows`,
  `documentation`, `tpm`, `product-design`, and `mental-models`.

### Skills

* git-workflows: changelog-generator, pr-review, pull-request
* documentation: documentation, strategic-design-doc
* tpm: jira-cli
* product-design: cognitive-load, fogg-behavior-mode, trust-psychology
* mental-models: five-why, graph-thinking, tit-for-tat

### Agents

* code-reviewer (git-workflows), design-doc (documentation)

### Documentation

* `talk` output style (mental-models)
