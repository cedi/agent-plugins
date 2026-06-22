#!/usr/bin/env bash
#
# install.sh — wire this repo's Agent Skills into the tools that read them.
#
# All four supported tools understand the open Agent Skills standard: a flat
# <name>/SKILL.md directory. Codex, OpenCode, and Cursor all read
# ~/.agents/skills, so a single per-skill symlink farm there covers all three.
# Claude Code is handled separately via the plugin marketplace (see README).
#
# This script is:
#   - idempotent  (re-running is safe; correct links are left as-is)
#   - additive    (never deletes skills it doesn't own; your dd-* and anything
#                  already present are preserved)
#   - explicit    (prints every action and SKIPs foreign entries)
#
# Usage:
#   ./install.sh                  # link the 12 skills into ~/.agents/skills
#   ./install.sh DIR [DIR...]     # link into explicit roots instead
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO/skills"

targets=("${@:-$HOME/.agents/skills}")

link_into() {
  local dir="$1"

  if [ -L "$dir" ]; then
    local resolved; resolved="$(cd "$dir" 2>/dev/null && pwd -P || true)"
    case "$resolved" in
      *"/.dotfiles/"*|*"/dotfiles/"*)
        echo "!! $dir is a symlink into your dotfiles ($resolved)."
        echo "   Refusing to write through it (would re-pollute dotfiles)."
        echo "   Convert it to a real directory first — see README."
        return 0 ;;
    esac
  fi

  mkdir -p "$dir"
  echo "==> $dir"
  local name target link
  for skill in "$SRC"/*/; do
    name="$(basename "$skill")"
    target="$SRC/$name"
    link="$dir/$name"
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then
      echo "    ok   $name"
    elif [ -e "$link" ] || [ -L "$link" ]; then
      echo "    SKIP $name (exists, not ours)"
    else
      ln -s "$target" "$link"
      echo "    link $name"
    fi
  done
}

for t in "${targets[@]}"; do
  link_into "$t"
done

echo
echo "Codex, OpenCode, and Cursor read ~/.agents/skills — they're now wired."
echo "For Claude Code, add the marketplace:"
echo "    claude plugin marketplace add $REPO"
