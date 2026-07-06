---
name: vault-curate
description: Use when the user wants to check the health of their Obsidian vault - orphaned notes, broken or dead wikilinks, missing backlinks, missing or malformed frontmatter, tag hygiene, or contradictions between notes. Triggers include "curate my vault", "vault health check", "find orphans", "find dead links", "lint my notes".
---

# vault-curate

Produce a vault health report and propose fixes. Read broadly, change nothing in
curated zones without approval. Provenance comes from git, not from log notes.

## Prerequisite

Read the vault conventions file (root `AGENTS.md` or `CLAUDE.md`) for the taxonomy,
per-type frontmatter schemas, tag and linking conventions, and the write-zone
policy. Use the obsidian MCP, and ripgrep over the vault where that is faster across
the whole vault.

## Checklist (report each as its own section)

1. Orphans: notes with no inbound and no outbound links.
2. Dead links: `[[wikilinks]]` that resolve to no existing note (compare the
   `links` metadata against actual files).
3. Missing backlinks: non-daily notes lacking the standard backlinks block.
4. Frontmatter gaps: notes missing `created`, the date tag, or the required
   fields for their type.
5. Tag hygiene: near-duplicate or singleton tags, notes missing their type tag.
6. Contradictions (judgment): notes asserting conflicting facts. Flag them, do
   not resolve them.

## Report format

For each finding give the note path, what is wrong, and the proposed fix. Group
by category, most actionable first, with per-category counts at the top.

## Fixes (ask first for curated zones)

A safe, mechanical fix in one of the conventions file's auto-write zones may be
applied directly. Anything in a curated zone must be proposed and confirmed first.
Batch related fixes into one confirmation. Obsidian Git records every change, so no
change-log note is needed.

## Output contract

A grouped report with counts and per-item proposed fixes. No edits to curated
notes without approval. Reads may span the whole vault.
