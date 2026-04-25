---
name: ship
description: >
  Use this skill when the user runs /ship, or says "ship it", "let's land this", "close out this
  sprint", "merge and tag", "push this out", "wrap up A3", or similar. Runs the sprint-loop
  closeout: quality gate, push, CI monitor, merge to default branch, checkpoint tag, backup
  branch, progress file deletion, STATE.md update, and final ship commit. Reads
  docs/sprint-loop.md frontmatter for the per-project toolchain config (lint/test/version-bump
  commands). Blocks if quality gate fails.
---

# /ship — sprint closeout

Close out the active sprint end-to-end. Follows the sequence in `docs/sprint-loop.md`, adapting
to the project's toolchain via that file's YAML frontmatter.

## Pre-flight

1. Read `docs/sprint-loop.md` frontmatter — extract `quality_gate`, `version_bump_command`,
   `ci_monitor_command`, `default_branch`, `checkpoint_convention`, `backup_branch_convention`.
2. Read `docs/local/STATE.md` Now section — extract stage, branch, progress file.
3. Run drift check (same logic as `/where`). If drift, surface and stop. Do not ship through drift.
4. Check `git status` — if uncommitted changes, ask: "commit these as part of the ship, or stash?"

## The ship sequence

1. **Quality gate.** Run every entry in `quality_gate` in order. On failure: diagnose, fix code
   (never fix the test to make it pass), re-run. Max 3 rounds before escalating to the user.
2. **Commit everything.** Ensure no uncommitted work remains on the branch.
3. **Version bump.** If `version_bump_command` is set, run it. Commit the bump with message
   `chore(<stage>): bump version`.
4. **User confirmation.** Before any network operation, show:
   - Branch being shipped
   - Commit count and summary
   - Version change (if any)
   - Target: `<default_branch>`
   Wait for explicit "yes" or "ship it".
5. **Push.** `git push origin <branch>`.
6. **CI monitor.** If `ci_monitor_command` is set, poll up to 10 minutes. On failure: diagnose,
   fix, repeat. Max 3 CI rounds before escalating.
7. **Merge.** Fast-forward merge into `<default_branch>`. No merge commits unless the user
   explicitly asks for one.
8. **Checkpoint.**
   - Annotated tag: `<checkpoint_convention>` with today's date and a short slug
     (e.g. `checkpoint-20260424-readiness-recovery`)
   - Backup branch: `<backup_branch_convention>` pointing at the just-merged default-branch HEAD
9. **Push tag and backup branch.**
10. **Final ship commit.** On `<default_branch>`, commit a message of the form:
    `ship: <stage>: <summary>`
    This commit may be empty (`git commit --allow-empty`) — its purpose is to mark the stage as
    complete in history and trigger the progress file deletion.
11. **Delete progress file(s).** `rm docs/local/progress/<hash>-*-<stage>-*.md`.
12. **Cleanup branches.** Delete local and remote feature branch.
13. **Empty temp.** `rm -rf docs/local/temp/*` if it exists.
14. **Update `docs/local/STATE.md`:**
    - Move Now entry into `Shipped this month` with tag, commit sha, date.
    - If completion plan has a next stage, move it into Now. Otherwise leave Now empty.
    - Update `Last updated` timestamp.
15. **Report.** One paragraph: what was shipped, tag name, version (if bumped), what's next.

## Principles

- **Fix code, never tests.** A failing test is a signal. Making it pass by changing it is a lie.
- **Never force-push.** Without explicit user permission, `--force` is forbidden.
- **Drift blocks the ship.** A session with drift is a session that hasn't been reconciled. Ship
  anyway and you cement the drift into history.
- **The ship commit is load-bearing.** It's what marks the stage done and triggers cleanup.
- **Backup before cleanup.** Tags and backup branches exist before any deletion.

## Escalation

Escalate to the user (don't retry silently) when:

- Quality gate fails 3 times in a row
- CI fails 3 times in a row
- Any network operation fails unexpectedly
- `git push` fails (could be auth, network, or a `--force` situation that requires consent)
