# Study Pass Findings: Existing Project-Management Infrastructure in `trading-system`

**Date:** 2026-04-24
**Scope:** Survey of project-management conventions, tools, and documents already present in `C:\Users\yury_\Downloads\project\traiding-system`. Purpose: ground the `project-log` skill design in a proven pattern rather than invent one.

---

## Summary

The trading-system repo contains a working three-tier project-management system that covers most of what we'd been designing for the `project-log` skill. The skill's job is therefore not to invent a design but to **generalize and package** this pattern so it can be applied to any new repo by a vibe coder.

This changes risk, effort, and shape of the remaining phases.

---

## What Exists

### Three-tier plan hierarchy

**Tier 1 — Overarching PRD.** `docs/PRD-v2.md` (25 KB).

Sections: Executive Summary, Product Thesis, Non-Negotiable Principles, Product Surfaces, capability requirement families with numbered IDs (GEM-01, GEM-02, …), Success Measures (G1–G6), **Maturity Scale** (level 0 "not started" → level 5 "expandable and stable"), **Product Progress Snapshot** table with per-workstream current level and "what moves it up one level" criterion, Pivot Rules, Roadmap Phases A/B/C/D, Improvements list, Non-Goals, Relationship to Existing Documents.

The maturity scale is a genuinely clever device: it makes progress measurable without ticket-estimate theater.

**Tier 2 — Mid-tier execution plans.**

- `docs/local/prd-v2-completion-plan-2026-04-20.md` (26 KB) — active Phase A/B completion plan. Decomposes PRD workstreams into ordered stages labeled `A3`, `B1`, etc.
- `docs/local/implementation-plan-2026-04-17.md` (10 KB) — implementation order reference.

These are the authoritative source of what-stage-is-next. The short stage IDs (`A3`, `B1`) are the mapping tokens that travel through branches, progress reports, and commits.

**Tier 3 — Tactical state + sprints.**

- `docs/local/STATE.md` (6 KB) — "what's active right now" with fixed sections:
  - **Now** — current branch, goal, status, blocker/next step
  - **Next** — queued items with pointers to completion plan
  - **Parked** — branches kept but not active, with reason
  - **Shipped this month** — recent merges with commit/version info
  - **Pointers** — durable references to PRD, runbooks, etc.
- `docs/local/progress/*` — per-effort progress reports, gitignored, deleted on ship.

### Progress report naming convention

```
<short-hash>-<YYYY-MM-DD>-<stage>-<slug>.md
```

Examples from the repo:
- `5258b3d-2026-04-23-a3-readiness-recovery-actions.md`
- `77ed9a7-2026-04-24-a3-pipeline-stale-alert-plan.md`
- `a3eed0a-2026-04-23-b1-finish-audit.md`

The `-a3-` / `-b1-` segment is the mapping token linking the progress file back to the stage in the completion plan, which itself links back to a workstream in PRD-v2. This is exactly the prefix/suffix mapping we discussed.

### Slash commands

Three commands in `.claude/commands/`, all load-bearing:

- **`/where`** — tactical "you are here" view. Reads STATE.md (intent) + git reality, reconciles them, flags drift if STATE.md is stale or if git reality doesn't match STATE.md's Now section. Output is a fixed ~15-line block. **This is the drift-check we designed, already implemented.**
- **`/roadmap`** — strategic one-page view. Reads PRD + completion plan + STATE.md + git tags, produces a progress table with `[✓ done] / [● now] / [○ next] / [○ later]` markers, plus "sprints remaining to v1.0" count.
- **`/idea`** — parking lot. Appends uncommitted ideas to `docs/local/ideas.md`. Keeps STATE.md Next section from filling with noise.

### Sprint loop

`docs/sprint-loop.md` (3 KB). Defines:
- Branching: `feat/<scope>-YYYY-MM-DD` or `fix/<scope>-YYYY-MM-DD`
- Quality gate: `uv run pre-commit run --all-files` + `uv run pytest`
- Version bump tied to branch prefix (`feat` → minor, `fix` → patch)
- Merge & checkpoint: fast-forward main, annotated tag `checkpoint-YYYYMMDD-<slug>`, backup branch `backup/main-after-YYYYMMDD-<slug>`
- Cleanup: delete merged branches (local + remote), empty `docs/local/temp/`
- Backup retention rules (keep tags forever, keep backup branches one sprint)

### Sprint-ship agent

`.claude/agents/sprint-ship.md` (18 KB). A full closeout agent with:
- Mission: run quality gate, follow sprint-loop, push, monitor CI, fix failures
- 6-phase workflow (read sprint-loop → pre-commit → git prep → user confirmation → push + monitor → completion)
- Critical rules (fix code not tests, never force-push without permission, etc.)
- Persistent agent memory at `.claude/agent-memory/sprint-ship/` with typed memory categories (user / feedback / project / reference)

### Supporting artifacts

- `CLAUDE.md` at repo root — short guide pointing Claude to STATE.md and sprint-loop.md.
- `PROJECT.md` at repo root — 1-paragraph note saying internal planning is not in public docs.
- `docs/local/README.md` — brief README for the local folder.
- `docs/local/progress/README.md` — documents the progress-report pattern.
- `docs/local/temp/` — scratch folder emptied at sprint closeout.

---

## What Is Transferable to the Skill

Most of it:

- **Three-tier plan hierarchy** (PRD → completion plan → sprints)
- **STATE.md shape** with Now / Next / Parked / Shipped / Pointers sections
- **Stage-ID mapping convention** (`[PHASE][NUMBER]` format, used in branch names, progress file names, commit messages)
- **Progress report naming convention** (hash-prefixed, dated, stage-tagged, slug)
- **Slash commands** `/where`, `/roadmap`, `/idea` — the patterns generalize cleanly
- **Sprint-ship agent structure** — its 6-phase workflow is tool-agnostic
- **Sprint-loop document shape** — branching, quality gate, closeout, cleanup, backup retention
- **Maturity scale** — highly transferable and unusually useful
- **Ideas parking lot** — discipline worth preserving
- **Persistent agent memory** — the 4-type taxonomy (user/feedback/project/reference) is a strong general pattern

---

## What Is Trading-System-Specific and Must Be Abstracted

These are the parts that would need to become per-project config:

- `uv run pre-commit run --all-files` → `{lint_command}`
- `uv run pytest` → `{test_command}`
- `trading-bump-version` / `make bump-version` → `{version_bump_command}` or disabled
- `robojob` / `gh run list` CI references → `{ci_monitor_command}` or disabled
- `python` / `pytest` / `ruff` / `mypy` tooling assumptions → generic "run your project's configured checks"
- Specific workstream names (Trading Engine, Gemma, etc.) — removed from the template

---

## Gaps the Skill Must Fill Beyond What Exists

Four gaps stand out:

### 1. Bootstrap workflow for a new project

The trading-system setup was built by hand over time. There is no documented, repeatable way to scaffold this structure on a fresh repo. The skill needs:

- A `/bootstrap` slash command (or its equivalent)
- A conversational interview that drafts the PRD from the user's idea
- Generation of the scaffold folders and templates
- Initial population of STATE.md and a first sprint

The user already confirmed the intake interview itself should be a conversation with Claude, not an automated wizard — but the skill should package the prompts and the scaffold.

### 2. Tool-stack abstraction

Sprint-loop and sprint-ship currently hardcode Python/uv tooling. The skill must separate "what the sprint loop does" (quality gate, version bump, merge, cleanup) from "which commands implement it" (per-project config).

### 3. Stage-ID convention formally declared

Currently the `[PHASE][NUMBER]` pattern (A3, B1) is implicit — it works because the user uses it consistently. The skill must codify it as a required convention so agents enforce it and users know how to use it on a new project.

### 4. Drift-check automation

`/where` exists but is invoked manually. The skill could enforce a drift check at specific moments (session start, before allowing new work to begin). This is a behavioral change, not a missing artifact.

---

## Recommended Naming Scheme for the Skill

Adopt the existing pattern verbatim. No reinvention.

**Progress reports** (gitignored, deleted on ship):
```
docs/local/progress/<hash>-<YYYY-MM-DD>-<stage>-<slug>.md
```

**Branches:**
```
feat/<stage>-<YYYY-MM-DD>
fix/<stage>-<YYYY-MM-DD>
```

**Commits:**
```
feat(<stage>): <summary>
fix(<stage>): <summary>
ship: <stage>: <summary>          ← commit that deletes the progress file
```

**Stage IDs:** `[PHASE][NUMBER]` format, where phase is a single uppercase letter A/B/C/... defined in the PRD's roadmap phases, and number is a small integer ordering the stage within the phase.

---

## Implications for the Phased Plan

The original 7-phase production plan assumed designing from scratch. Given this finding, the revised phase list is:

1. ✓ Study pass
2. Extract transferable patterns + gap analysis (this document)
3. Draft revised PRD for project-log skill
4. Produce first-cut skill folder
5. Dry run on a throwaway repo
6. Iterate skill to v2
7. Field test on a real new project
8. Refine skill to production v3
9. [OPTIONAL] Build VS Code extension wrapper

Phase 3 (PRD) is much lower-risk now — we're writing a spec for something we've seen work, not an invention. Phases 4-6 remain the same shape but should be faster because the core design is validated.

---

## Open Design Decisions for the Revised PRD

1. **One skill or two?** Bootstrap (intake + scaffold) could be a separate skill from project-log (ongoing execution). Leaning: one skill, two modes, because a vibe coder shouldn't have to remember which to invoke.
2. **Where does tool-stack config live?** Options: a dedicated `.projectlog/config.yml`, inline inside `docs/sprint-loop.md`, or fields in STATE.md's Pointers block. Leaning: inside `docs/sprint-loop.md` as a front-matter block, so the loop doc is self-contained.
3. **Does the skill ship with `/where`, `/roadmap`, `/idea` commands?** Or document them as "install these commands alongside"? Leaning: ship them as part of the skill folder.
4. **Maturity scale mandatory or optional?** It's clever enough that mandatory has appeal, but it's heavier than some projects need. Leaning: mandatory, but with a simplified 3-level default (Not started / In progress / Done) that users can expand.
