#!/bin/bash
# Weekly vault review draft job. Runs headless claude with a prompt stored in the
# vault, drafts the result into the vault's inbox, and never writes curated zones.
#
# Configuration (vault-agnostic; nothing personal is hardcoded):
#   OBS_VAULT             absolute path to your Obsidian vault (required)
#   CLAUDE_BIN            path to the claude binary (optional; default: claude on PATH)
#   REVIEW_PROMPT_NOTE    vault-relative path to the prompt note
#                         (optional; default: "Meta/Weekly Vault Review.md")
#
# These may be exported in the environment, or set in a runner env file at
#   ${VAULT_SKILLS_RUNNER_CONFIG:-$HOME/.config/vault-skills/runner.env}
# which is sourced if present. Keep that file out of any public repo.
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

RUNNER_CONFIG="${VAULT_SKILLS_RUNNER_CONFIG:-$HOME/.config/vault-skills/runner.env}"
[ -f "$RUNNER_CONFIG" ] && . "$RUNNER_CONFIG"

: "${OBS_VAULT:?set OBS_VAULT (env or $RUNNER_CONFIG) to your Obsidian vault path}"
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude || echo "$HOME/.local/bin/claude")}"
REVIEW_PROMPT_NOTE="${REVIEW_PROMPT_NOTE:-Meta/Weekly Vault Review.md}"

VAULT="$OBS_VAULT"
NOTE="$VAULT/$REVIEW_PROMPT_NOTE"
LOG="${VAULT_SKILLS_LOG:-$HOME/.claude/logs/weekly-vault-review.log}"

mkdir -p "$(dirname "$LOG")"
echo "=== run $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

[ -f "$NOTE" ] || { echo "prompt note missing: $NOTE" >> "$LOG"; exit 1; }
[ -x "$CLAUDE_BIN" ] || { echo "claude binary missing: $CLAUDE_BIN" >> "$LOG"; exit 1; }

# The prompt is the FIRST fenced code block in the note; commentary lives outside it.
# (The prompt itself must not contain a ``` fence.)
PROMPT=$(awk '/^```/{c++; next} c==1{print}' "$NOTE")
[ -n "${PROMPT//[[:space:]]/}" ] || { echo "empty prompt, aborting" >> "$LOG"; exit 1; }

"$CLAUDE_BIN" -p "$PROMPT" --dangerously-skip-permissions >> "$LOG" 2>&1
RC=$?
echo "claude exit: $RC" >> "$LOG"

osascript -e 'display notification "Weekly review drafted to the vault inbox (review + promote)" with title "Vault weekly review"' >/dev/null 2>&1 || true
exit "$RC"
