---
name: log
description: >
  Use this skill when the user runs /log, or says "log this", "note that", "I just shipped X",
  "I'm blocked on Y", "we just decided Z", "parking this branch", "we're unblocked", or any
  variant of capturing a one-line milestone. Also auto-invoke whenever the coding agent itself
  recognizes that a milestone just occurred — a new branch was created for a stage, a non-obvious
  decision was made, a blocker appeared or resolved, or a branch is being parked. Appends one
  line to docs/local/project-log.md in the canonical format. Never edits existing entries. Ship
  events are written by /ship; replan events by /replan; this skill handles everything else.
---

# /log — milestone capture

Append a single milestone line to `docs/local/project-log.md`. The project-log is append-only and
never edited — every entry is the durable narrative.

## When to fire

Either the user explicitly invokes (slash command or natural phrasing), **or** the coding agent
recognizes a milestone just happened. Per principle 9 (PRD §3), the agent owns milestone capture
and should fire this skill at the moment, not retrospectively.

Milestone kinds (each writes one line):

| Kind | When to write |
|---|---|
| `started` | A new branch is created for a stage (`git checkout -b feat/<stage>-…`). Auto-fired by the agent. |
| `decision` | A non-obvious technical or product call worth flagging for future readers. |
| `blocker` | Work cannot progress without external input or upstream resolution. |
| `unblock` | A previously logged blocker is resolved. |
| `parked` | A branch is being parked rather than shipped. |
| `note` | Anything else worth a one-liner. Use sparingly — keep signal high. |
| `shipped` | **Written by `/ship`. Do not write here.** |
| `replan` | **Written by `/replan`. Do not write here.** |

## What to do

1. **Determine the kind.** From the user's phrasing or from context. If ambiguous, ask one
   short question; do not guess.
2. **Determine the stage.** Read the current STATE.md Now section, or infer from the active
   branch name (`feat/<stage>-…` → `<stage>` in uppercase). If neither yields a stage, ask.
3. **Construct the line** in the canonical format from PRD §5.3:
   ```
   <ISO-8601 timestamp>  <stage>  <kind>  <one-line description>  [→ <pointer>]
   ```
   - Timestamp: UTC, format `YYYY-MM-DDThh:mmZ`. Use the system clock.
   - Stage: uppercase letter + integer (e.g. `A3`, `B1`).
   - Kind: from the table above.
   - Description: one short sentence. No newlines. No markdown.
   - Pointer (optional): branch name, commit sha, checkpoint tag, progress-file path, CI run id —
     whatever the most useful breadcrumb is for that kind. Prefix with `→ `.
4. **Idempotency check.** Before appending, read the last ~5 lines of `docs/local/project-log.md`.
   If the same `<stage>  <kind>  <description>` appeared within the last few minutes, do NOT
   append a duplicate — confirm to the user with `already logged: <existing line>` and stop.
5. **Append the line** to `docs/local/project-log.md`. If the file doesn't exist, create it from
   `../project-log/templates/project-log.md` first, then append.
6. **Confirm to the user** with a one-line acknowledgement:
   `logged: <stage> <kind> — <description>`

## Examples

User says: "I just branched feat/a4-self-improvement-guardrails-2026-04-25 for A4."
→ append:
```
2026-04-25T14:20Z  A4  started   branch feat/a4-self-improvement-guardrails-2026-04-25
```

User says: "Decided to route AutoResearch through the parameter_change_queue instead of auto-applying."
→ append:
```
2026-04-25T16:10Z  A4  decision  route AutoResearch through parameter_change_queue, not auto-apply
```

User says: "Blocked — CI run 24921142480 was cancelled by the version bump."
→ append:
```
2026-04-25T18:05Z  A4  blocker   CI run 24921142480 cancelled — version bump superseded
```

Agent observes a previously logged blocker resolve:
→ append:
```
2026-04-25T19:00Z  A4  unblock   CI green on retry — run 24921797794
```

## Principles

- **One milestone, one line.** No multi-line entries. If it doesn't fit, it's two milestones — or
  it belongs in the per-effort progress file as a longer note, not in the project-log.
- **At the moment, not retrospectively.** Write when it happens. Batching at session end loses
  the timestamps' meaning.
- **Append-only.** Never edit existing entries, even to fix typos. Mistakes get a follow-up
  `note` line.
- **Stage required.** Every entry needs a stage ID. If you can't determine one, ask the user
  before writing.
- **Skip `shipped` and `replan`.** Those are owned by `/ship` and `/replan` respectively. Writing
  them here would create duplicates.
- **Quiet acknowledgement.** Confirm with one line. Don't summarize the log or read entries
  back unsolicited.
