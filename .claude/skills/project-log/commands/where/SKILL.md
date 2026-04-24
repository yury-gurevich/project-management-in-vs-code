---
name: where
description: >
  Use this skill when the user runs /where or asks "where am I", "where are we", "what's the
  current state", "status", or any variant asking for a quick tactical snapshot of the active
  sprint. Produces a ~15-line block reconciling docs/local/STATE.md against git reality. Read-only
  — never writes files. If STATE.md and git disagree, flags the mismatch so the user can fix it
  before more work happens.
---

# /where — tactical "you are here" view

Produce a compact block showing:

- current branch, current stage, status, blocker
- next-up (1–3 bullets from STATE.md's Next)
- parked count
- last shipped (from STATE.md's Shipped)
- staleness flag (STATE.md last-updated > 3 days)
- mismatch flag (STATE vs git)

## What to do

1. Read `docs/local/STATE.md`. If missing, emit a single-line message: `STATE.md not found — run /bootstrap to initialize`.
2. Run these git commands and capture output:
   - `git branch --show-current`
   - `git status --short | head -20`
   - `git log --oneline -5`
3. Reconcile. Mismatch patterns to flag:
   - **Branch mismatch** — current branch differs from STATE.md's Now branch
   - **Stale progress** — STATE.md's Now references a progress file that doesn't exist
   - **Uncommitted work on parked branch** — dirty tree on a branch STATE.md marks parked/shipped
   - **Stale STATE.md** — last-updated field is more than 3 days old
4. Emit the output block in the exact format below. No prose outside it.

## Output format

```
── where ──────────────────────────────────────────────
stage:       <A3>
branch:      <feat/a3-...-2026-04-23>
status:      <one-line status from STATE.md Now>
blocker:     <one-line blocker or "none">
next up:     <up to 3 bullets from Next>
parked:      <count> branch(es)
shipped:     <most recent entry from Shipped this month>
stale?       <yes (reason) | no>
mismatch?    <none | list of specific mismatches>
──────────────────────────────────────────────────────
```

## Principles

- **Read-only.** Never write files. If reconciliation is needed, point the user at `/replan` or tell them to update STATE.md manually.
- **One block.** No prose before or after. The user should be able to paste this into Slack or an email.
- **~15 lines.** If the block grows past 20 lines, trim Next or Shipped to the most-recent entries.
