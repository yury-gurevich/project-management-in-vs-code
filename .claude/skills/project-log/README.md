# project-log — Install & Use

A Claude skill that adds narrative project management to any coding repo.

## What you get

- Three-tier plan system: **PRD → completion plan → STATE.md + sprints**
- Stage-ID mapping (`A3`, `B1`, …) tying branches, commits, and progress files back to the PRD
- Slash commands: `/bootstrap`, `/where`, `/roadmap`, `/idea`, `/replan`, `/ship`
- Drift detection between STATE.md and git reality on session start
- "Delete on ship" — transient files cleaned up, permanent record in git history

## Install

### Per-project

```bash
cp -r .claude/skills/project-log /path/to/your-project/.claude/skills/
```

Open the target project in Claude Code or Cowork. The skill activates automatically.

### User-level (all projects)

- **Linux / macOS:** `~/.claude/skills/project-log/`
- **Windows Cowork:** `%APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\<session>\<plugin>\skills\project-log\`

## First use — bootstrap

1. `cd` into an empty or near-empty repo.
2. Open a Claude session.
3. Run `/bootstrap`.
4. Answer the interview questions.
5. Claude drafts `docs/PRD.md`, `docs/sprint-loop.md`, and seeds `docs/local/STATE.md`.
6. Review, edit, approve.
7. Start your first sprint.

## Daily use

- **Session start:** drift check runs automatically. Fix any flagged mismatches.
- **While working:** commit with stage prefixes (`feat(a3): …`). Update the progress file on material changes only.
- **Status:** `/where` (tactical) or `/roadmap` (strategic).
- **Idea for later:** `/idea` drops into the parking lot.
- **Direction changed:** `/replan`.
- **Stage done:** `/ship` — quality gate, push, tag, cleanup.

## License

MIT.
