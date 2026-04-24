# project-management-in-vs-code

A Claude skill that adds narrative project management to any coding repo — **PRD → completion plan → STATE.md + sprints**, with drift detection and one-command progress reports.

Designed for solo developers working with autonomous coding agents (Claude Code, Cowork). Not a team tracker. No tickets, no boards, no integrations.

## The problem

Vibe-coding with an autonomous agent produces a lot of motion but very little legible progress. After a week you can't answer "where are we", "what's shipped", "what's next". The agent drifts from the plan without anyone noticing.

## The solution

Three tiers of plan, one skill that enforces the discipline.

```
docs/PRD.md                                  ← what we're building, phases, success criteria
docs/local/completion-plan-YYYY-MM-DD.md     ← phases decomposed into ordered stages (A1, A2, B1…)
docs/local/STATE.md                          ← what's active right now
docs/local/progress/*.md                     ← per-sprint working notes (deleted on ship)
```

Every sprint carries a stage ID through branches, commits, and progress file names. Drift between `STATE.md` and `git` is detected on session start. Shipping runs your quality gate, tags a checkpoint, and deletes the transient files.

## Slash commands

| Command | What it does |
|---|---|
| `/bootstrap` | Conversational PRD intake + scaffold for a fresh project |
| `/where` | Tactical "you are here" view — ~15 lines |
| `/roadmap` | Strategic one-page view — ~25 lines |
| `/idea` | Parking-lot capture (keeps STATE.md focused) |
| `/replan` | Structured PRD revision with change log |
| `/ship` | Quality gate, push, tag, cleanup, STATE update |

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
