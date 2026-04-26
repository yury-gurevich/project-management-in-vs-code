---
name: roadmap
description: >
  Use this skill when the user runs /roadmap or asks "what's the big picture", "what's the plan",
  "how much is left", "when will we ship v1", or any variant asking for a strategic progress view.
  Produces a ~25-line one-page block summarizing PRD phases, current stage, progress table with
  done/now/next/later markers, sprints remaining to v1.0, parked count, and ideas parked.
  Read-only — never writes files.
---

# /roadmap — strategic one-page view

Produce a compact block covering the whole project.

## What to do

1. Read in order:
   - `docs/PRD.md` — extract vision (one line), Phases A/B/C/…, success measures
   - `docs/local/completion-plan-*.md` (most recent) — extract stage list
   - `docs/local/project-log.md` (full file, or last 200 entries if longer) — extract `started`,
     `shipped`, `blocker`, `unblock`, `replan`, `parked` counts; this is the durable history
   - `docs/local/STATE.md` — extract Now, Next, Parked sections (cross-check against project-log)
   - `docs/local/ideas.md` — count entries
2. Run `git tag --list 'checkpoint-*' | wc -l` and `git log --oneline --grep='^ship:' | wc -l` for ship count.
3. Estimate sprints-remaining as: total stages in completion plan minus stages already shipped.
4. Emit the output block below.

## Output format

```
── roadmap ────────────────────────────────────────────
vision:      <one line from PRD executive summary>
today:       <YYYY-MM-DD>  version: <from git tags or "pre-v1">
phase:       <current phase letter and theme>
active:      <Now stage + one-line goal>
blocker:     <Now blocker or "none">

progress:
  Phase A — <theme>
    [✓] A1  <one-line summary>      shipped <date>
    [✓] A2  <one-line summary>      shipped <date>
    [●] A3  <one-line summary>      active
    [○] A4  <one-line summary>      next
  Phase B — <theme>
    [○] B1  <one-line summary>      later
    [○] B2  <one-line summary>      later

sprints remaining to v1.0: <N>
parked:                     <count>
ideas parked:               <count>

notes:       <one or two lines if anything notable; else omit>
──────────────────────────────────────────────────────
```

## Markers

- `[✓]` — shipped
- `[●]` — active (current Now stage)
- `[○]` — not started
- `[◆]` — parked

## Principles

- **Read-only.** Never write files.
- **One page.** ~25 lines. If the progress table is longer than 15 rows, truncate the oldest shipped stages with an ellipsis.
- **Pasteable.** A human should be able to send this to a stakeholder as-is.
