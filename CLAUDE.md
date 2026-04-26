# Project Notes for Claude

This repo *is* the `project-log` skill. It also dogfoods itself — the same scaffolding the skill
installs in consumer repos lives here under `docs/`. When working in this repo, treat the skill's
own discipline as load-bearing.

## Session start

Before touching any code:

1. Read the tail of [`docs/local/project-log.md`](docs/local/project-log.md) — the canonical
   append-only history. The latest `started`-without-`shipped` entry tells you the active stage.
2. Read [`docs/local/STATE.md`](docs/local/STATE.md) — derived snapshot of "right now."
3. Read the active per-effort progress file's tail (under `docs/local/progress/`) — the last
   `Next:` line is the resume cursor.
4. Run `git status --short`, `git branch --show-current`, `git log --oneline -5`.
5. Reconcile. If STATE.md and the project-log disagree, the project-log wins; regenerate STATE.md.

Shortcut: run `/where` to get a one-block reconciliation that does steps 1–5 in one shot.

## Closing a stage

Use `/ship`. It reads [`docs/sprint-loop.md`](docs/sprint-loop.md) for this repo's toolchain
(currently a very light quality gate — see frontmatter) and runs the full sequence: quality gate,
push, merge, checkpoint tag, backup branch, distil per-effort progress to project-log, delete
progress file, regenerate STATE, ship commit.

## Planning

- Strategic: [`docs/PRD.md`](docs/PRD.md) — v1.1, approved, v0.2 build complete, v1.0 in flight.
- Tactical: [`docs/local/completion-plan-2026-04-26.md`](docs/local/completion-plan-2026-04-26.md)
  — Phase C is the active phase (v1.0 readiness).
- Canonical history: [`docs/local/project-log.md`](docs/local/project-log.md) (append-only,
  never edited).
- Day-to-day: [`docs/local/STATE.md`](docs/local/STATE.md) (derived) +
  `docs/local/progress/*.md` (resume cursor for active sprint).

## Milestone capture

Every meaningful state transition (started a branch, made a non-obvious decision, hit a blocker,
got unblocked, parked a branch) gets one line in
[`docs/local/project-log.md`](docs/local/project-log.md). Use `/log` or just describe it ("I'm
blocked on X", "decided to use Y") — the agent will write the canonical line. Ship and replan
events are written automatically by `/ship` and `/replan`.

## Docs layout

- `docs/` — tracked, public, long-lived (PRD, sprint-loop, study findings, future runbooks).
- `docs/local/` — gitignored. Long-lived local state (project-log, STATE, completion plans, ideas).
- `docs/local/progress/` — per-effort progress reports, hash-prefixed, deleted on ship.
- `docs/local/temp/` — scratch, emptied at sprint closeout.

When generating working files that aren't authoritative, write to `docs/local/temp/` by default.
Only promote to `docs/local/` or `docs/` when content becomes load-bearing.

## Stage IDs

Format: `[PHASE][N]` — e.g. `C1`, `C2`. Phase letter from the completion plan; integer orders
stages within the phase. This ID propagates into branches, commits, progress file names, and
project-log entries.

## Direction changes

If scope, principles, or phase ordering need to change, run `/replan` rather than editing the
PRD quietly. `/replan` adds a timestamped entry to the PRD Revision Log, regenerates the
completion plan, and writes a `replan` line to the project-log.

## Parking lot

Ideas that aren't for now: `/idea` captures them into `docs/local/ideas.md`. Keeps STATE.md's
Next queue focused on stages we've actually committed to.

## Dogfood notes

- The skill's own definitions live under `.claude/skills/`. Edits here ship the skill; treat
  them as production changes, not scratch work.
- Each sibling skill is also exposed as a slash-command shim under `.claude/commands/`. When
  adding/removing a sibling skill, update both places.
- Templates that ship to consumer repos live at `.claude/skills/project-log/templates/`. Changes
  there are user-visible — note them in PRD §13 Revision Log if the contract changes.
