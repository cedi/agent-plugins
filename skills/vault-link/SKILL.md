---
name: vault-link
description: Use when the user wants to strengthen the connections in their Obsidian vault by finding and adding missing wikilinks from a note to related existing notes. Triggers include "link this note", "find related notes", "connect this to the graph", "what should this link to", "densify my graph".
---

# vault-link

Densify the vault graph by proposing the wikilinks a note is missing. Finds absent
links, the complement to vault-curate which finds broken ones.

## Prerequisite

Read the vault conventions file (root `AGENTS.md` or `CLAUDE.md`) for the linking
conventions (`[[wikilinks]]` vs `related_documents` frontmatter, aliases) and the
write-zone policy. Use the obsidian MCP.

## Recipe

1. Target: the note the user names, or the active/most-recent note. A folder batch
   is allowed but process one note at a time.
2. Extract the note's salient entities and concepts: people, projects, tools,
   incidents, and topics it discusses.
3. For each, search the vault for an existing note that matches and that the target
   does not already link. Propose only genuinely related notes; ignore near-misses.
4. Propose specific edits: inline `[[wikilink]]` insertions (quote the sentence and
   show where the link goes) and/or `related_documents` frontmatter additions,
   whichever the convention fits. Do not over-link; a few right links beat many weak
   ones.
5. Apply after approval. Curated zones are ask-first; in every zone preserve the
   surrounding text exactly and only insert the link.

## Output contract

A short list of proposed links, each with the target note, the exact insertion point
or frontmatter field, and why it is relevant. No edits to curated notes without
approval. No over-linking, and never a link to a note that does not exist.
