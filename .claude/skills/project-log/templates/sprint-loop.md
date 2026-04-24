---
# Tool-stack config — edit these values for your project.
# The skill reads this frontmatter to adapt the sprint loop to your stack.

quality_gate:
  - name: lint
    command: "<your lint command, e.g. ruff check . && ruff format --check .>"
  - name: test
    command: "<your test command, e.g. pytest>"

version_bump_command: null          # e.g. "make bump-version" or leave null
ci_monitor_command: null            # e.g. "gh run list --limit 1" or leave null
default_branch: main
checkpoint_convention: "checkpoint-YYYYMMDD-<slug>"
backup_branch_convention: "backup/main-after-YYYYMMDD-<slug>"
---

# Sprint Loop

Every sprint follows the same loop: branch → work → quality gate → push → merge → checkpoint →
cleanup. The skill enforces this shape; the YAML above adapts it to your toolchain.

## 1. Branching

Branch names encode the stage and date:

```
feat/<stage>-<YYYY-MM-DD>
fix/<stage>-<YYYY-MM-DD>
```

- `feat/` → minor version bump on ship
- `fix/` → patch version bump on ship

Examples: `feat/a3-readiness-recovery-2026-04-23`, `fix/b1-alert-noise-2026-04-24`.

## 2. Quality gate

Run every command in `quality_gate` (from frontmatter above) until all pass. Fix code, not tests.
Lint warnings and test failures are both blockers — no exceptions.

## 3. Commit cadence

Commits are stage-prefixed:

```
feat(<stage>): <summary>
fix(<stage>): <summary>
```

Commit as often as the active sprint plan says to — the skill does not enforce a cadence.

## 4. Push & merge

1. Push the branch.
2. If `ci_monitor_command` is set, watch CI. If red, fix. Max 3 rounds before escalating to the user.
3. Fast-forward merge to `default_branch` (no merge commits unless explicitly requested).

## 5. Checkpoint

After merge:

- Annotated tag: `<checkpoint_convention>` — e.g. `checkpoint-20260424-readiness-recovery`
- Backup branch: `<backup_branch_convention>` — e.g. `backup/main-after-20260424-readiness-recovery`

Tags are kept forever. Backup branches are kept one sprint and then deleted.

## 6. Ship commit

The final commit of a ship uses a distinct form to mark the stage as completed:

```
ship: <stage>: <summary>
```

This commit is also the trigger that deletes the sprint's progress file (see step 8).

## 7. Version bump

If `version_bump_command` is set, run it after checkpoint. Otherwise skip.

## 8. Cleanup

- Delete the local and remote feature branch after merge.
- Delete `docs/local/progress/<hash>-<date>-<stage>-*.md` for the shipped stage.
- Empty `docs/local/temp/` if it exists.

## 9. Update STATE.md

- Move the Now entry into `Shipped this month`.
- If there's a next stage in the completion plan, move it into Now. Otherwise leave Now empty.
- Update the `Last updated` timestamp.
