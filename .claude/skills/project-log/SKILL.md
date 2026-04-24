---
name: project-log
description: >
  Use this skill whenever the user is working on a coding project that needs narrative project
  management. Triggers include: starting a new project, asking "where are we" / "what's next" /
  "what's shipped", shipping a sprint, updating project state, producing a progress report,
  recovering from drift between plan and git reality, or installing project-log scaffolding into
  a repo that doesn't have it yet. Also trigger when the user mentions a "PRD", "completion plan",
  "STATE.md", "sprint loop", or slash commands like /where, /roadmap, /idea, /bootstrap, /replan,
  /ship. This skill is a discipline layer for solo developers working with autonomous coding
  agents — not a team tracker.
---

# project-log — Narrative Project Management for Solo Coders

`project-log` is a three-tier project-management discipline packaged as a Claude skill. It keeps a
solo developer and an autonomous coding agent aligned on **where the project is, what's next, and
what's shipped** — without tickets, boards, or team ceremony.

## When to use this skill

Invoke this skill's behaviors whenever any of these are true:

- The user asks about project status ("where are we", "what's next", "what's shipped")
- The user is starting a new project or adding project-log to an existing repo
- The user wants to ship, replan, or park something
- A session is opening on a repo that has a `docs/PRD.md` + `docs/local/STATE.md` pair
- The user mentions a PRD, completion plan, sprint loop, stage ID, or a slash command
  (`/where`, `/roadmap`, `/idea`, `/bootstrap`, `/replan`, `/ship`)

## The three-tier model

| Tier | Artifact | Purpose | Lives in git? |
|---|---|---|---|
| 1 | Overarching **PRD** | Vision, principles, success measures, maturity scale, roadmap phases | Yes (`docs/PRD.md`) |
| 2 | **Completion plan** | Ordered decomposition of PRD into stages `A1`, `A2`, `B1` … | No (`docs/local/completion-plan-YYYY-MM-DD.md`) |
| 3 | **STATE + sprints** | What's active right now, progress reports per sprint | No (`docs/local/STATE.md`, `docs/local/progress/*.md`) |

Stage IDs (`[PHASE][N]` — e.g. `A3`, `B1`) are the **mapping token** linking branches, commits, and
progress files back to the PRD.

```
Branch:        feat/a3-readiness-recovery-2026-04-23
Progress file: docs/local/progress/5258b3d-2026-04-23-a3-readiness-recovery.md
Commit:        feat(a3): add readiness self-recovery
Ship commit:   ship: a3: readiness self-recovery landed
```

## Non-negotiable principles

1. **Narrative over tickets.** STATE.md is a living story, not a queue.
2. **Single source of truth per tier.** PRD is vision, completion plan is ordering, STATE.md is now.
3. **Mapping tokens everywhere.** Every sprint, branch, progress file, and commit carries the stage ID.
4. **Delete on ship.** Progress reports are transient; permanent record lives in git history + STATE.md.
5. **Drift check is mandatory.** Session start reconciles STATE.md against `git` reality before any work.
6. **The tool is dumb; the plan is smart.** Slice size and commit cadence live in the active plan, not in this skill.
7. **Intake is conversational.** Bootstrap is a dialogue with Claude, not a form.

## What to do at session start

Run this check in order before touching any code:

1. Read `docs/local/STATE.md` if it exists.
2. Run `git status --short`, `git branch --show-current`, `git log --oneline -5`.
3. Reconcile STATE.md's **Now** section against git reality. Mismatch patterns:
   - Current branch differs from STATE.md's Now branch → flag
   - Uncommitted changes on a parked/shipped branch → flag
   - No progress file exists for the Now sprint → flag
   - STATE.md's "last updated" is > 3 days old → flag
4. If any mismatch → surface it and block new work until reconciled.
5. If no mismatch → read the Now sprint's progress file and continue from there.
6. If no `docs/PRD.md` exists at all → prompt the user to run `/bootstrap`.

## Commands (nested skills)

| Command | What it does |
|---|---|
| `/bootstrap` | Conversational PRD intake + scaffold generation for a fresh project |
| `/where` | Tactical "you are here" view — reconciles STATE.md vs git, ~15 lines |
| `/roadmap` | Strategic one-page view — PRD + phases + sprints remaining, ~25 lines |
| `/idea` | Parking-lot capture to `docs/local/ideas.md` |
| `/replan` | Structured revision of the PRD with change-log entry + completion-plan regen |
| `/ship` | Ship protocol — quality gate, push, merge, checkpoint, delete progress, update STATE |

Each command is a nested skill at `.claude/skills/project-log/commands/<name>/SKILL.md`.

## Filename conventions (enforced)

```
docs/PRD.md                                                          # tracked
docs/local/completion-plan-YYYY-MM-DD.md                             # gitignored
docs/local/STATE.md                                                  # gitignored
docs/local/progress/<shortsha>-YYYY-MM-DD-<stage>-<slug>.md          # gitignored, deleted on ship
docs/local/ideas.md                                                  # gitignored parking lot
docs/sprint-loop.md                                                  # tracked, per-project tool config
```

## Tool-stack abstraction

`docs/sprint-loop.md` has a YAML frontmatter block the skill reads to adapt to any stack. See
`templates/sprint-loop.md` for the canonical shape. Edit the frontmatter; leave the body alone.

## What this skill is NOT

- Not a ticket tracker (no Jira, Linear, GitHub Issues sync)
- Not a team product (one user, one repo)
- Not a code-quality tool (that's lint/tests, configured via sprint-loop frontmatter)
- Not a strategic advisor — it won't tell you what to build, only help you stay on plan
