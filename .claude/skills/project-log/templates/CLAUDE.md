# Project Notes for Claude

## Session start

Before touching any code:

1. Read the tail of [`docs/local/project-log.md`](docs/local/project-log.md) — the canonical
   append-only history. The latest `started`-without-`shipped` entry tells you the active stage.
2. Read [`docs/local/STATE.md`](docs/local/STATE.md) — derived snapshot of "right now."
3. Read the active per-effort progress file's tail — the last `Next:` line is the resume cursor.
4. Run `git status --short`, `git branch --show-current`, `git log --oneline -5`.
5. Reconcile. If STATE.md and the project-log disagree, the project-log wins; regenerate STATE.md.

Shortcut: run `/where` to get a one-block reconciliation that does steps 1–5 in one shot.

## Closing a stage

Use `/ship`. It reads [`docs/sprint-loop.md`](docs/sprint-loop.md) for your toolchain and runs
the full sequence: quality gate, push, CI monitor, merge, checkpoint tag, backup branch, progress
file cleanup, STATE.md update.

## Planning

- Strategic: [`docs/PRD.md`](docs/PRD.md)
- Tactical: `docs/local/completion-plan-<date>.md`
- Canonical history: `docs/local/project-log.md` (append-only, never edited)
- Day-to-day: `docs/local/STATE.md` (derived) + `docs/local/progress/*.md` (resume cursor)

## Milestone capture

Every meaningful state transition (started a branch, made a non-obvious decision, hit a blocker,
got unblocked, parked a branch) gets one line in [`docs/local/project-log.md`](docs/local/project-log.md).
Use `/log` or just describe it ("I'm blocked on X", "decided to use Y") — the agent will write
the canonical line. Ship and replan events are written automatically by `/ship` and `/replan`.

## Docs layout

- `docs/` — tracked, public, long-lived (PRD, sprint-loop, runbooks fit for publication)
- `docs/local/` — gitignored, long-lived local notes
- `docs/local/progress/` — per-effort progress reports, hash-prefixed, deleted on ship
- `docs/local/temp/` — scratch, emptied at sprint closeout

When generating working files that aren't authoritative, write to `docs/local/temp/` by default.
Only promote to `docs/local/` or `docs/` when content becomes load-bearing.

## Stage IDs

Format: `[PHASE][N]` — e.g. `A3`, `B1`. Phase letter from PRD roadmap Phases, integer orders
stages within the phase. This ID propagates into branches, commits, and progress file names.

## Direction changes

If scope, principles, or phase ordering need to change, run `/replan` rather than editing the PRD
quietly. `/replan` adds a timestamped entry to the PRD Revision Log and regenerates the completion
plan.

## Parking lot

Ideas that aren't for now: `/idea` captures them into `docs/local/ideas.md`. Keeps STATE.md Next
section focused.
