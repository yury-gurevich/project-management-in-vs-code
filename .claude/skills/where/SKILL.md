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
- next-up (1–3 bullets — primary source is the active progress file's last `Next:` line)
- parked count
- last shipped (latest project-log `shipped` entry)
- staleness flag (project-log latest entry > 3 days)
- mismatch flag (STATE vs project-log vs git)

## What to do

1. Read `docs/local/project-log.md`. If missing, emit: `project-log.md not found — run /bootstrap to initialize`.
2. Read `docs/local/STATE.md` if it exists.
3. Read the tail (~30 lines) of the active per-effort progress file referenced by the latest
   `started`-without-a-`shipped` entry in project-log. The last `Next:` line is the resume cursor.
4. Run these git commands and capture output:
   - `git branch --show-current`
   - `git status --short | head -20`
   - `git log --oneline -5`
5. Reconcile. Mismatch patterns to flag:
   - **Wrong-repo refuse (HARD)** — STATE.md's `Repo root` field doesn't match
     `git rev-parse --show-toplevel` (case-insensitive, slash-normalized). This is a hard refuse
     — emit the mismatch block and stop. Do not regenerate STATE, do not produce the standard
     `── where ──` block. The session is in the wrong repo (or STATE.md is from another repo).
   - **Branch mismatch** — current branch differs from the latest project-log `started` entry
     that hasn't been `shipped` yet
   - **Stale progress** — project-log marks a stage active but no progress file exists for it
   - **Uncommitted work on shipped branch** — dirty tree on a branch the project-log marks as shipped
   - **Stale project-log** — latest entry is more than 3 days old (likely missing milestones)
   - **STATE drift** — STATE.md's Now disagrees with the project-log tail
   - **No clean cursor** — active progress file's last entry has no `Next:` line
   - **Missing Repo root field (SOFT)** — STATE.md exists but has no `**Repo root:**` header line
     (predates C3). Note this once in the output; suggest the user add the line. Do not refuse.
6. If **STATE drift** is the only mismatch, regenerate STATE.md's Now and Shipped sections from
   the project-log tail + active progress file (this is the *only* file write `/where` ever performs;
   warn the user that hand-edits to those sections will be overwritten). For all other mismatches,
   surface and stop.
7. Emit the output block in the exact format below. No prose outside it.

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

- **Almost read-only.** The only write `/where` ever performs is regenerating STATE.md's Now and
  Shipped sections from the project-log when STATE drift is detected. Never edits the project-log,
  PRD, completion plan, progress files, or anything else.
- **The project-log is canonical.** STATE.md is a derived view. When they disagree, the project-log
  wins.
- **One block.** No prose before or after. The user should be able to paste this into Slack or an email.
- **~15 lines.** If the block grows past 20 lines, trim Next or Shipped to the most-recent entries.
