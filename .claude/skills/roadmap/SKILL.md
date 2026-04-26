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

1. **Decide mode.** Check the project-log size before reading: `wc -l docs/local/project-log.md`
   and `head -1`'s timestamp.
   - **Full mode** (default): file is < 500 lines AND first entry is < 6 months old → read the
     whole file, render every shipped/active stage in the progress table.
   - **Roll-up mode**: either threshold breached → split the log at the cutoff (see step 2) and
     compress the older half into a single bullet group above the per-stage table.
2. Read in order:
   - `docs/PRD.md` — extract vision (one line), Phases A/B/C/…, success measures.
   - `docs/local/completion-plan-*.md` (most recent) — extract stage list.
   - `docs/local/project-log.md` — read scope depends on mode:
     - **Full mode**: read everything.
     - **Roll-up mode**: read everything but split into "recent" and "older" halves.
       The recent half is **the last 30 days OR the last 50 entries, whichever covers more**
       lines (so we always have meaningful context). The older half feeds the roll-up summary.
   - `docs/local/STATE.md` — extract Now, Next, Parked sections (cross-check against project-log).
   - `docs/local/ideas.md` — count entries.
3. Run `git tag --list 'checkpoint-*' | wc -l` and `git log --oneline --grep='^ship:' | wc -l` for ship count.
4. Estimate sprints-remaining as: total stages in completion plan minus stages already shipped.
5. Emit the output block below. In roll-up mode, insert the **rolled up** sub-block above
   `progress:` per the format below.

## Output format

**Full mode** (no roll-up):

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

**Roll-up mode** (project-log ≥ 500 lines OR ≥ 6 months old):

```
── roadmap ────────────────────────────────────────────
vision:      <one line from PRD executive summary>
today:       <YYYY-MM-DD>  version: <from git tags or "pre-v1">
phase:       <current phase letter and theme>
active:      <Now stage + one-line goal>
blocker:     <Now blocker or "none">

rolled up (<N> log lines, <M> stages, before <YYYY-MM-DD>):
  Phase A — <theme>
    [✓] A1  <shipped one-liner>      shipped <date>
    [✓] A2  <shipped one-liner>      shipped <date> — 2 decisions, 1 blocker resolved
    [✓] A3  <shipped one-liner>      shipped <date>
  Phase B — <theme>
    [✓] B1  <shipped one-liner>      shipped <date>
    [◆] B2  <last decision/note>      parked since <date>
  (notes & blocker/unblock pairs aggregated; <K> notes, <P> blocker pairs not enumerated)

progress (recent <recent-window-description>):
  Phase C — <theme>
    [✓] C4  <one-line summary>      shipped <date>
    [●] C5  <one-line summary>      active
    [○] C6  <one-line summary>      next

sprints remaining to v1.0: <N>
parked:                     <count>
ideas parked:               <count>

notes:       <one or two lines if anything notable; else omit>
──────────────────────────────────────────────────────
```

The `recent <recent-window-description>` line states which window the user is seeing:
e.g. `recent (last 50 entries — covers 2026-04-26..2026-05-12)` or `recent (last 30 days)`.

## Markers

- `[✓]` — shipped
- `[●]` — active (current Now stage)
- `[○]` — not started
- `[◆]` — parked

## Roll-up compression rules

When in roll-up mode, the older half of the project-log compresses to **one line per stage**
following these rules:

- **Shipped stage** → `[✓] <stage>  <shipped one-liner>  shipped <date>` plus an optional
  ` — N decisions, M blockers resolved` suffix when those counts are non-zero. Use the message
  text from the `shipped` log entry verbatim where it fits.
- **Active stage** still in the rolled-up half (rare — implies a stage open > 6 months) →
  `[●] <stage>  <last decision or note as one-liner>  active since <date>`.
- **Parked stage** → `[◆] <stage>  <last decision or note as one-liner>  parked since <date>`.
- **`note` entries** → never enumerated. Counted in the aggregate footer:
  `(notes & blocker/unblock pairs aggregated; <K> notes, <P> blocker pairs not enumerated)`.
- **`blocker`/`unblock` pairs** → counted, not enumerated. An unmatched `blocker` (no later
  `unblock`) becomes a one-line note in the stage's row: `... — open blocker: <description>`.
- **`replan` entries** → counted, with the **most recent** reason preserved as a footnote at
  the bottom of the rolled-up block: `(last replan <YYYY-MM-DD>: <reason>)`.

Within the rolled-up block, group stages by phase letter (Phase A, Phase B, …) the same way
the full progress table does. Truncate phases that span > 8 stages by showing the first 3 +
`... + N more` + the last 2.

## Principles

- **Read-only.** Never write files.
- **One page.** ~25 lines in full mode; ~30 in roll-up mode (the rolled-up block adds ~5).
  If the progress table is still too long after roll-up, truncate the oldest shipped stages
  with an ellipsis.
- **Pasteable.** A human should be able to send this to a stakeholder as-is.
- **Project-log stays append-only.** Roll-up is a *render* transformation. Never delete, archive,
  or rewrite project-log entries (per PRD §3 principle 4).
- **Mode is observable.** Always include the `rolled up (...)` header in roll-up mode so the
  reader knows they're seeing a compressed view, not the whole story.
