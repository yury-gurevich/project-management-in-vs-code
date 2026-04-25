---
description: Sprint closeout — quality gate, push, merge, tag, cleanup, STATE update
---

Use the `ship` skill from `.claude/skills/ship/SKILL.md` to run the sprint-loop closeout sequence. Read `docs/sprint-loop.md` frontmatter for the per-project toolchain (lint/test/version-bump). Block if quality gate fails. Steps: quality gate → push → CI monitor → merge to default → checkpoint tag → backup branch → delete progress file → update STATE.md → final ship commit.
