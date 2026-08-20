---
name: vault-capture
description: Use when the user wants to capture something into their Obsidian vault - a note, thought, decision, meeting, PR discussion, clipping, person, or reference - including quick captures made from inside another repo. Triggers include "capture this", "save to my vault", "note this in obsidian", "add to my second brain".
---

# vault-capture

Turn a piece of raw input into one well-filed, well-linked note in the Obsidian
vault, honoring the vault's own conventions and its write-zone fences.

## Prerequisite

Read the vault's conventions file (its root `AGENTS.md` or `CLAUDE.md`) for the
folder taxonomy, per-type frontmatter schemas, tag and linking conventions, writing
style, and the write-zone policy (which folders are auto-write, ask-first, or
read-only). This skill does not restate them; follow that file. The vault location
comes from your obsidian MCP or global config. Use the obsidian MCP's search and
write tools so writes flow through Obsidian and get auto-committed.

## Recipe

1. Classify the input: which note type (daily, clipping, decision or project-doc,
   person, incident, tool, reference) and therefore which folder.
2. Pick the target by the conventions file's write-zone policy:
   - Auto-write zone: write directly.
   - Ask-first (curated) zone: propose the full path and content, wait for approval.
   - Unsure, or a quick cross-repo capture with no obvious home: default to the
     vault's inbox / auto-write staging zone and name the likely home in the body.
3. Search the vault first for one to three related existing notes to link.
4. Compose the note:
   - Frontmatter matching the per-type schema. Always include `created:` and the
     date tag the conventions file specifies.
   - Body in the vault's writing style.
   - At least one `[[wikilink]]` to a related note found in step 3.
   - For non-daily notes, add the standard backlinks block if the conventions file
     defines one.
5. Write a new note, or append/patch into an existing note or a daily section, via
   the obsidian MCP.
6. Report the exact path written and the links added.

## Output contract

One note. Correct folder for its type. Valid per-type frontmatter including the
date tag. At least one wikilink. Curated zones are never written without approval.
Writing-style rules obeyed.

## Common mistakes

- Writing to a curated zone without asking. Propose and wait instead.
- Inventing facts to fill a schema field. Leave it out; a short accurate note wins.
- Markdown links instead of `[[wikilinks]]` for internal references.
- Forgetting the date tag or the backlinks block.
