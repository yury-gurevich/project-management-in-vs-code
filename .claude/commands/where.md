---
description: Tactical "you are here" view — reconciles STATE.md vs git, ~15 lines
---

Use the `where` skill from `.claude/skills/where/SKILL.md` to produce a tactical status block. Read `docs/local/STATE.md`, run `git status --short`, `git branch --show-current`, and `git log --oneline -5`, then output the ~15-line block defined in that skill. Flag any mismatches between STATE.md's "Now" section and git reality.
