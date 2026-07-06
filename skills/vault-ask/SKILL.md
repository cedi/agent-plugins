---
name: vault-ask
description: Use when the user asks a question that should be answered from their Obsidian vault - recalling decisions, people, projects, incidents, or prior notes - rather than from general knowledge. Triggers include "what do my notes say about", "who is", "what did we decide on", "search my vault for", "ask my vault".
---

# vault-ask

Answer a question from the vault by searching, following links, and synthesizing a
cited answer. Read-only: it never writes.

## Prerequisite

Read the vault conventions file (root `AGENTS.md` or `CLAUDE.md`) for the taxonomy
and linking conventions. Use the obsidian MCP's search, and ripgrep over the vault
where that is faster. `Personal/` is read-only-when-relevant; respect it.

## Recipe

1. Decompose the question into search terms and the note types likely to hold the
   answer (person, project, incident, decision, tool, daily).
2. Search several angles, not one: full-text (obsidian search / ripgrep), title,
   and tag. For a broad or multi-part question, fan out ONE subagent per angle and
   have each return a compact list of candidate notes with one-line relevance, so
   the raw hits never flood the main context.
3. Read the most relevant notes, and follow their backlinks and outlinks one hop to
   catch context the keyword search missed.
4. Synthesize a direct answer, matching the reasoning to the question. For a causal
   "why" question, work to the root cause rather than the first surface statement
   (the five-why approach). For a "how do these relate, what depends on what, where
   is the leverage" question, reason over the connections rather than a flat list
   (the graph-thinking approach). Cite every claim with the `[[note]]` it came from,
   and a block or heading reference where precision matters.
5. Be honest about coverage: name what the vault does not say rather than filling
   the gap, and flag notes that contradict each other instead of silently picking one.

## Output contract

A direct, cited answer grounded only in vault content. Every non-trivial claim links
to its source note. Gaps and contradictions surfaced, not papered over. Nothing is
written; if the user wants the answer saved, hand off to `vault-capture`.
