# project-log skill — memory directory

Cross-session memory for the `project-log` skill. The agent reads `MEMORY.md` at session start and writes new entries here whenever it learns something durable about the user, the project, or how the skill is being used.

## Why this exists

Some Claude harnesses (e.g. Claude Code) provide an auto-memory system at the harness level — those memories live outside any individual skill and survive across all conversations and projects.

This in-skill memory is the **portable fallback** for harnesses that don't have one (Cowork, raw Claude Desktop, raw API). When both exist, treat them as parallel: the harness's auto-memory wins for general user context; the in-skill memory captures discipline-specific knowledge (e.g. "this user prefers C-stages of size ≤ small," "this user's PRD style favors shorter principles lists") that ought to ride along with the skill itself.

When the skill is installed user-level (`~/.claude/skills/project-log/`), this memory survives across every project the user touches with the skill. When the skill is installed project-level (`.claude/skills/project-log/`), it's per-project. Either way it's per-install, and personal entries never leak into the skill's source repo (gitignore enforces this).

## Types of memory

Mirrors the 4-type taxonomy used by harness auto-memory so an agent that already knows one knows both.

| Type | What it captures | Example trigger |
|---|---|---|
| **user** | Role, preferences, responsibilities, knowledge level. Helps tailor explanations and suggestions. | "I'm a data scientist, this is my first time touching the React side of this repo." |
| **feedback** | Approach guidance — both corrections AND validated successes. Lead with the rule, then **Why:** and **How to apply:** lines. | "Don't auto-ship sprints with <3 acceptance criteria — last time we shipped half-built." OR "Yeah, the single bundled commit was the right call here." |
| **project** | Ongoing initiatives, deadlines, who's blocked on what. State changes fast — keep it current. Convert relative dates to absolute. | "We're freezing non-critical merges after Thursday — the trading-system rebuild needs the runway." |
| **reference** | Pointers to where information lives in external systems. | "Pipeline bugs are tracked in Linear project INGEST." OR "The grafana board at grafana.internal/d/api-latency is what oncall watches." |

## How to write an entry

Two-step process per entry:

1. **Write the memory file** in this directory using `_TEMPLATE.md` as the starting point. Name it after the topic, not the date — e.g. `user_role.md`, `feedback_ship_size.md`, `project_q2_freeze.md`, `reference_linear_ingest.md`.
2. **Add a one-line index entry** to `MEMORY.md` pointing at the new file.

Frontmatter required on every entry file:

```markdown
---
name: <short title>
description: <one line — used to decide relevance later, so be specific>
type: user | feedback | project | reference
---
```

Body conventions:

- **feedback** and **project** entries: lead with the rule/fact, then a `**Why:**` line (the reason — often a past incident) and a `**How to apply:**` line (when this kicks in). Knowing *why* lets future-you judge edge cases.
- **user** entries: short — role, current focus, what to tailor.
- **reference** entries: pointer + when to consult it.

## When NOT to save

- Code patterns, file paths, architecture — re-derivable by reading the project.
- Git history / who-changed-what — `git log` / `git blame` are authoritative.
- Debugging fixes — the fix is in the code; the commit message has the context.
- Anything already in `CLAUDE.md` or the PRD.
- Ephemeral conversation state.

These exclusions hold even when the user asks to save such things. If they ask, ask back: what was *surprising* or *non-obvious* — that's the part worth keeping.

## When to read

- Session start (the main `project-log` SKILL.md does this).
- Before answering a question that depends on user preferences, prior corrections, or active project state.
- When the user references prior-conversation work explicitly.

If the user says "ignore memory" or "don't use memory" — comply: don't apply, cite, or compare against memory in that turn.

## Staleness

Memory entries can become wrong over time. Before recommending an action based purely on memory:

- If the memory names a file path: confirm the file still exists.
- If the memory names a function or flag: grep for it.
- If the memory describes project state ("we're in freeze," "X is blocked on Y"): verify it's still true before acting.

When current state contradicts memory, trust observation and update or remove the stale entry.

## Files in this directory

- `README.md` — this file. Tracked.
- `_TEMPLATE.md` — entry template. Tracked.
- `MEMORY.md` — index of entries. Header tracked, entries gitignored.
- `<type>_<topic>.md` — individual memory entries. Gitignored.
