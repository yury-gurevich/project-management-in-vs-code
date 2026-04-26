# project-management-in-vs-code

A Claude skill that adds narrative project management to any coding repo — **PRD → completion plan → project-log + per-effort progress → derived STATE**, with drift detection and one-command progress reports.

Designed for solo developers working with autonomous coding agents (Claude Code, Cowork). Not a team tracker. No tickets, no boards, no integrations.

## The problem

Vibe-coding with an autonomous agent produces a lot of motion but very little legible progress. After a week you can't answer "where are we", "what's shipped", "what's next". The agent drifts from the plan without anyone noticing.

## The solution

A small set of plan files, a discipline the agent maintains itself, and one append-only history file (`project-log.md`) that survives every ship.

```
docs/PRD.md                                  ← what we're building, phases, success criteria
docs/local/completion-plan-YYYY-MM-DD.md     ← phases decomposed into ordered stages (A1, A2, B1…)
docs/local/project-log.md                    ← append-only lifetime milestone log (canonical history)
docs/local/progress/*.md                     ← per-sprint working notes (resume cursor; deleted on ship)
docs/local/STATE.md                          ← derived "what's active now" snapshot
```

Every sprint carries a stage ID through branches, commits, progress file names, and project-log entries. The agent writes a one-line milestone to `project-log.md` at every meaningful transition (started, decision, blocker, unblock, parked, shipped). Drift between the project-log and `git` is detected on session start. Shipping runs your quality gate, tags a checkpoint, distils the per-effort progress file into one project-log line, then deletes the progress file.

## Slash commands

| Command | What it does |
|---|---|
| `/bootstrap` | Conversational PRD intake + scaffold for a fresh project |
| `/where`     | Tactical "you are here" view — ~15 lines, reconciles STATE vs project-log vs git |
| `/roadmap`   | Strategic one-page view — ~25 lines |
| `/idea`      | Parking-lot capture (keeps STATE.md focused) |
| `/log`       | Append a one-line milestone to `project-log.md` |
| `/replan`    | Structured PRD revision with Revision Log entry + completion-plan regen |
| `/ship`      | Quality gate, push, tag, distil progress to project-log, cleanup, STATE regen |

Each slash command also fires from natural phrasing ("where are we", "I'm blocked on X", "ship it") — the user does not need to remember which one to type.

## Install

### Into a target project

```bash
cp -r .claude/skills/project-log /path/to/your-project/.claude/skills/
```

### Into your Claude user skills

- **Linux / macOS:** `~/.claude/skills/project-log/`
- **Windows (Cowork):** `%APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\<session>\<plugin>\skills\project-log\`

A helper script for Windows Cowork: [`scripts/install-to-plugin.ps1`](scripts/install-to-plugin.ps1).

## Status

Early preview. Works in the author's personal `trading-system` repo (which inspired the design). This repo is the generalized, portable version.

## Design rationale

Full PRD at [`docs/PRD.md`](docs/PRD.md). Study findings that led to the design at [`docs/study-findings.md`](docs/study-findings.md).

## License

MIT.
