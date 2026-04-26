---
description: Append a one-line milestone to docs/local/project-log.md (kind auto-detected)
argument-hint: <kind?> <description>
---

Use the `log` skill from `.claude/skills/log/SKILL.md` to append a milestone line to `docs/local/project-log.md`. Parse `$ARGUMENTS` for the kind (`started`, `decision`, `blocker`, `unblock`, `parked`, `note`) and the description; if no kind is given, infer from phrasing. Determine the stage from STATE.md or the active branch, construct the canonical line, idempotency-check the tail, then append. Confirm with `logged: <stage> <kind> — <description>`.
