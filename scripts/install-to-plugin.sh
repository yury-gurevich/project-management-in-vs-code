#!/usr/bin/env bash
# Install the project-log skill into ~/.claude/skills/ so it's visible in every Claude session.
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$REPO_ROOT/.claude/skills/project-log"
DEST="${HOME}/.claude/skills/project-log"

if [[ ! -d "$SOURCE" ]]; then
    echo "ERROR: skill source not found at $SOURCE" >&2
    exit 1
fi

mkdir -p "$(dirname "$DEST")"

if [[ -d "$DEST" ]]; then
    read -rp "Destination $DEST exists. Overwrite? (y/N) " ans
    [[ "$ans" == "y" ]] || { echo "Aborted."; exit 0; }
    rm -rf "$DEST"
fi

cp -r "$SOURCE" "$DEST"
echo "Installed to $DEST"
echo "Restart your Claude session to pick up the new skill."
