# Project Notes for Claude

## Session start

Before touching any code:

1. Read [`docs/local/STATE.md`](docs/local/STATE.md) — the single source of truth for what's active.
2. Run `git status --short`, `git branch --show-current`, `git log --oneline -5`.
3. Reconcile. If STATE.md and git disagree, fix STATE.md before proceeding.

Shortcut: run `/where` to get a one-block reconciliation.

## Closing a stage

Use `/ship`. It reads [`docs/sprint-loop.md`](docs/sprint-loop.md) for your toolchain and runs
the full sequence: quality gate, push, CI monitor, merge, checkpoint tag, backup branch, progress
file cleanup, STATE.md update.

## Planning

- Strategic: [`docs/PRD.md`](docs/PRD.md)
- Tactical: `docs/local/completion-plan-<date>.md`
- Day-to-day: `docs/local/STATE.md` + `docs/local/progress/*.md`

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
