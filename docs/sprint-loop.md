---
# Tool-stack config — this is a markdown / skill-definition repo, no code or test harness yet.
# Quality gate is light: whitespace + formal structure of changed skill files.
# When/if a markdown linter or skill-package validator is added, wire it in here.

quality_gate:
  - name: whitespace
    command: "git diff --check HEAD"
  - name: skill-frontmatter-present
    command: "grep -L '^name:' .claude/skills/*/SKILL.md && exit 1 || exit 0"

version_bump_command: null          # No semver yet. Skill package version lives in PRD frontmatter.
ci_monitor_command: null            # No CI configured yet.
default_branch: main
checkpoint_convention: "checkpoint-YYYYMMDD-<slug>"
backup_branch_convention: "backup/main-after-YYYYMMDD-<slug>"
---

# Sprint Loop

Every sprint follows the same loop: branch → work → quality gate → push → merge → checkpoint →
cleanup. The skill enforces this shape; the YAML above adapts it to this repo's (currently very
light) toolchain.

## 1. Branching

Branch names encode the stage and date:

```
feat/<stage>-<short-slug>-<YYYY-MM-DD>
fix/<stage>-<short-slug>-<YYYY-MM-DD>
```

- `feat/` → for any stage from the completion plan (Cn, Dn, etc.)
- `fix/` → for bugs found in shipped stages

Examples: `feat/c2-skill-self-memory-2026-04-26`, `fix/c1-bootstrap-typo-2026-04-27`.

Bootstrap (the `/bootstrap` act itself) is the one exception: it lands on `main` directly, since
it pre-dates the discipline it installs.

## 2. Quality gate

Run every command in `quality_gate` (from frontmatter above) until all pass. For this repo right
now the gate is intentionally minimal:

- **whitespace** — no trailing whitespace or mixed-indent lines in the diff.
- **skill-frontmatter-present** — every `SKILL.md` has the required `name:` field at the top.

Treat any future additions (markdown lint, skill-package validator, link checker) as adding rows
to this gate, not replacing it.

## 3. Commit cadence

Commits are stage-prefixed:

```
feat(<stage>): <summary>
fix(<stage>): <summary>
docs(<stage>): <summary>      # for PRD or template-only changes
chore(<stage>): <summary>     # for non-functional skill changes
```

Commit as often as the active sprint plan says to — the skill does not enforce a cadence.

## 4. Push & merge

1. Push the branch.
2. Once CI exists (`ci_monitor_command` set), watch it. Until then, manual smoke: run `/where`
   and confirm no drift, then proceed.
3. Fast-forward merge to `main`. No merge commits unless explicitly requested.

## 5. Checkpoint

After merge:

- Annotated tag: `checkpoint-YYYYMMDD-<slug>` — e.g. `checkpoint-20260426-c1-self-host-bootstrap`
- Backup branch: `backup/main-after-YYYYMMDD-<slug>`

Tags are kept forever. Backup branches are kept one sprint and then deleted.

## 6. Ship commit

The final commit of a ship uses a distinct form:

```
ship: <stage>: <summary>
```

This commit may be empty (`git commit --allow-empty`) — its purpose is to mark the stage complete
in history.

## 7. Version bump

`version_bump_command` is null for now — the skill package version lives in the PRD frontmatter
(`Version: 1.1 (skill package v0.2)`). When v1.0 ships, decide whether to bump via PRD `/replan`
or to add a real version file + bump command here.

## 8. Cleanup

- Delete the local and remote feature branch after merge.
- Delete `docs/local/progress/<hash>-*-<stage>-*.md` for the shipped stage.
- Empty `docs/local/temp/` if it exists.

## 9. Distil to project-log + regenerate STATE.md

- `/ship` reads the per-effort progress file, writes one `shipped` line to
  `docs/local/project-log.md`, then deletes the progress file.
- STATE.md's Now and Shipped sections are regenerated from the project-log tail.
- User picks the next stage from STATE.md's Next queue.
