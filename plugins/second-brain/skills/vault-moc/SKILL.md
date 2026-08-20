---
name: vault-moc
description: Use when the user wants to build or refresh a Map of Content or topic overview in their Obsidian vault, summarizing where a topic stands and keeping the index current. Triggers include "update the MOC", "state of this project", "summarize this topic", "refresh the map of content", "roll up these notes".
---

# vault-moc

Maintain a Map of Content: synthesize where a topic stands across its notes, and
keep the index structure current. Preserves existing Dataview blocks and manual
curation; it augments, never clobbers.

## Prerequisite

Read the vault conventions file (root `AGENTS.md` or `CLAUDE.md`) for the MOC
frontmatter schema, the standard Dataview aggregator patterns, and tag and linking
conventions. MOCs are curated (ask-first). Use the obsidian MCP.

## Recipe

1. Scope: an existing MOC note, or a tag/folder that defines the topic. Gather the
   member notes (reuse the MOC's Dataview query if it has one; otherwise scan).
2. Synthesis (state of X): read the member notes and write a short prose overview of
   where the topic stands now - current status, open threads, recent changes, key
   decisions - with `[[wikilinks]]` to the notes each point draws on. Model the topic
   as a system, not a flat list: surface dependencies, clusters, bottlenecks, and
   second-order effects (the graph-thinking lens). This is what Dataview cannot
   produce.
3. Structural hygiene: ensure correct MOC frontmatter (moc tag, date,
   related_documents), sensible section grouping, and no stale manual links; keep
   every existing Dataview block intact.
4. Never duplicate what a Dataview block already lists; let the query do the listing
   and place your synthesis above it.

## Write (ask first)

MOCs are curated. Show the proposed synthesis and any structural edits against the
exact target path, then apply after approval. Update in place; preserve manual
curation and Dataview blocks.

## Output contract

An updated MOC with a current state-of-topic synthesis and clean structure, Dataview
blocks and manual curation preserved, approved before writing. No invented status;
summarize only what the member notes actually say.
