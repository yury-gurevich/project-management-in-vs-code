#!/usr/bin/env bash
# Copies the project-log skill + its 7 slash-command siblings to ~/.claude/skills/
# Preserves personal memory entries on reinstall (only scaffold files are overwritten).
set -euo pipefail

SKILL_NAMES=(project-log where roadmap idea bootstrap replan ship log)
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/.claude/skills"
TARGET="$HOME/.claude/skills"

mkdir -p "$TARGET"
echo "Source: $SKILLS_SRC"
echo "Target: $TARGET"

for name in "${SKILL_NAMES[@]}"; do
    src="$SKILLS_SRC/$name"
    dst="$TARGET/$name"
    if [[ ! -d "$src" ]]; then
        echo "  [!] skipping $name — not found"
        continue
    fi
    # Merge-copy (do NOT rm -rf $dst): overwrites same-named files, leaves
    # everything else (e.g. user's personal memory/<type>_*.md entries) untouched.
    mkdir -p "$dst"
    cp -R "$src/." "$dst/"
    echo "  [+] $name"
done
echo "Done. Restart your Claude Code session."
