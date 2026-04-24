# PRD: `project-log` Skill

**Version:** 1.0 draft
**Date:** 2026-04-24
**Status:** Pending approval
**Owner:** Yury Gurevich
**Grounded in:** `project_log_study_findings.md` (2026-04-24)

---

## 1. Executive Summary

`project-log` is a Claude Code skill that brings disciplined, narrative-driven project management to any coding repository. It packages a proven three-tier pattern — **overarching PRD → mid-tier completion plan → tactical sprint state** — so a solo developer working with an autonomous coding agent can maintain a living story of the project (what's shipped, what's active, what's next) and produce concise progress reports on demand.

It is not a ticket tracker, a board, or a team product. It is a single-user narrative-and-discipline layer that sits on top of Claude Code or Cowork. Its job is to ensure that an autonomous agent working on a project always knows where it is, what it is supposed to do next, and surfaces drift when intent diverges from reality.

The pattern is validated: it already runs in production inside the `trading-system` repo. This skill generalizes it for use on any new project.

---

## 2. Product Thesis

A solo developer using an autonomous coding agent should be able to:

- Start a brand-new project from a vague idea and end up with a structured PRD, an ordered execution plan, and a working scaffold — via conversational interview, not boilerplate typing.
- Trust that the agent will not drift far from the plan without the drift being surfaced explicitly.
- Hand someone a short progress report — for themselves, a stakeholder, or a future reader — without hand-writing it.
- Carry the same workflow from one project to the next, so discipline doesn't have to be reinvented each time.

---

## 3. Non-Negotiable Principles

1. **Narrative over tickets.** State is a living story, not a queue of discrete units.
2. **Single source of truth per tier.** PRD for vision, completion plan for ordering, STATE.md for current state. No shadow sources.
3. **Mapping tokens everywhere.** Every sprint, branch, progress file, and commit carries the stage ID linking it back to the PRD.
4. **Delete on ship.** Sprint plans and progress reports are transient; permanent record lives in git history + STATE.md's Shipped section + PRD maturity progression.
5. **Drift check is mandatory.** At session start and at every state transition, the skill reconciles STATE.md against git reality.
6. **The tool is dumb; the plan is smart.** Slice size, commit cadence, and ship criteria live in the active sprint plan, not hardcoded in the skill.
7. **Intake is conversational, not automated.** Bootstrap is a dialogue with Claude, not a wizard. The skill packages the prompts and the scaffold templates, but the judgment lives in the conversation.

---

## 4. Scope

### In scope (v1)

- Conversational bootstrap workflow for new projects (`/bootstrap`)
- Three-tier plan layout + STATE.md maintenance
- Stage-ID mapping enforcement across filenames, branches, commits
- Drift check on session start + on state transition
- Sprint execution loop (plan → work → ship)
- Ship protocol with automatic progress-file cleanup
- Progress report generation on demand (`/where`, `/roadmap`)
- Ideas parking lot (`/idea`)
- Tool-stack config abstraction via `docs/sprint-loop.md` frontmatter
- Nested skills for slash-command-style invocation

### Out of scope (v1)

- Multi-user / team features
- Issue tracker sync (GitHub Issues, Jira, Linear)
- Payments, resource allocation, Gantt charts
- Automated time tracking
- Cross-repo rollup (one repo = one project, per user decision)
- VS Code extension (deferred to Phase 9, conditional on field-test success)

### Explicit non-goals (never in scope)

- A chat-first "what should I build today" assistant — this is a discipline layer, not a product strategist
- Auto-execution without intake (there must always be a PRD)
- Team collaboration surfaces

---

## 5. Architecture

### 5.1 Three-tier plan hierarchy

| Tier | Artifact | Purpose | Location | Lifecycle |
|---|---|---|---|---|
| 1 | Overarching plan | Vision, principles, requirements, success measures, **maturity scale**, roadmap phases | `docs/PRD.md` | Tracked in git. Rarely rewritten. Evolves via explicit `/replan`. |
| 2 | Completion plan | Ordered decomposition of PRD into stages labeled `[PHASE][N]` | `docs/local/completion-plan-<YYYY-MM-DD>.md` | Gitignored. Evolves with each phase. Replaced (not edited) on major direction shifts. |
| 3 | State & sprints | What's active now, what's next, what's shipped | `docs/local/STATE.md` + `docs/local/progress/*.md` | Gitignored. Updated at every transition. Progress files deleted on ship. |

### 5.2 Stage-ID convention

- **Format:** `[PHASE][N]` — single uppercase letter A/B/C/..., then small integer.
- Phase letters come from PRD roadmap Phases (Phase A, Phase B, etc.).
- Integer orders stages within a phase.
- Examples: `A1`, `A3`, `B1`, `C2`.

Stage IDs propagate into:

- **Branch names:** `feat/<stage>-<YYYY-MM-DD>`, `fix/<stage>-<YYYY-MM-DD>`
- **Progress file names:** `<hash>-<YYYY-MM-DD>-<stage>-<slug>.md`
- **Commit messages:** `feat(<stage>): <summary>`, `fix(<stage>): <summary>`, `ship: <stage>: <summary>`

### 5.3 STATE.md structure

Fixed sections (in order):

1. **Header** — last updated (by Claude), brief "how to read" note
2. **Now** — current branch, goal, status, blocker / next step
3. **Next** — queued stages with pointers to completion plan
4. **Parked** — branches kept but not active, with reason
5. **Shipped this month** — recent merges with stage / commit / version info
6. **Pointers** — durable references (PRD, completion plan, sprint-loop, runbooks)

### 5.4 Sprint-loop contract & tool-stack config

`docs/sprint-loop.md` holds the per-project tactical workflow. The skill reads its **YAML frontmatter** to adapt to any project's toolchain:

```yaml
---
quality_gate:
  - name: lint
    command: "<lint command>"
  - name: test
    command: "<test command>"
version_bump_command: "<optional>"
ci_monitor_command: "<optional>"
default_branch: main
checkpoint_convention: "checkpoint-YYYYMMDD-<slug>"
---
```

The body of `sprint-loop.md` then documents branching, quality gate, version closeout, merge/checkpoint, cleanup — generically, with placeholders referring back to the frontmatter values.

### 5.5 Maturity scale

The PRD template ships with a **mandatory 3-level default** maturity scale:

| Level | Meaning |
|---|---|
| 0 | Not started |
| 1 | In progress |
| 2 | Done |

Users can expand to a richer scale (e.g., the 0-5 scale the trading-system PRD uses) as their project grows. The default keeps vibe-coder-friendly projects simple; expansion is optional.

---

## 6. Skill Structure

```
project-log/
├── SKILL.md                      main entry; triggers on session start
├── README.md                     install instructions for the user
├── templates/
│   ├── PRD.md                    PRD template with maturity scale skeleton
│   ├── completion-plan.md        stage list template
│   ├── STATE.md                  state file template
│   ├── sprint-loop.md            sprint-loop with config frontmatter
│   ├── progress-report.md        in-flight progress template
│   └── CLAUDE.md                 project-level Claude pointer template
└── commands/                     nested skills; invocable as slash commands
    ├── where/SKILL.md            "you are here" view with drift reconciliation
    ├── roadmap/SKILL.md          one-page strategic progress view
    ├── idea/SKILL.md             parking-lot capture to ideas.md
    ├── bootstrap/SKILL.md        conversational PRD intake + scaffold generation
    ├── replan/SKILL.md           structured revision of the PRD with change log
    └── ship/SKILL.md             ship protocol: commit, delete progress, update STATE
```

### 6.1 Invocation

- **Main SKILL.md** auto-triggers when Claude opens the repo and the skill is installed.
- **Nested skills** invoke as slash commands (`/where`, `/roadmap`, `/idea`, `/bootstrap`, `/replan`, `/ship`).
- Per the Claude Code documentation, nested skills are the recommended path for slash-command-style behaviors — they work consistently across Cowork, Claude Code CLI, and Claude Desktop.

---

## 7. Workflows

### 7.1 Bootstrap (new project)

**Trigger:** user runs `/bootstrap`, OR main SKILL.md detects no `docs/PRD.md` on session start.

**Steps:**

1. Claude confirms the user wants to bootstrap (not, say, add project-log to an existing tracked project).
2. Claude interviews the user conversationally: what are you building, for whom, what is success, what constraints, what stack?
3. Claude drafts `docs/PRD.md` using the template (executive summary, principles, capabilities, success measures, mandatory 3-level maturity scale, roadmap Phases).
4. User reviews, edits, approves.
5. Claude drafts `docs/local/completion-plan-<date>.md` decomposing PRD Phase A into stages `A1`, `A2`, etc.
6. Claude creates `docs/local/STATE.md` with stage A1 seeded as Now.
7. Claude creates `docs/sprint-loop.md` with a starter frontmatter config (user fills in exact commands for their stack).
8. Claude installs project-level `CLAUDE.md` pointing future Claude sessions to STATE.md + sprint-loop.
9. Bootstrap complete; first sprint ready to execute.

### 7.2 Sprint execution

**At session start:**

1. Main SKILL.md reads STATE.md.
2. Runs drift check against git reality (same logic as `/where`).
3. If drift detected, surfaces it and blocks further work until reconciled or explicitly overridden.
4. If no Current sprint defined, prompts user to pick the next stage from Next.
5. Otherwise, reads active sprint's progress file and continues.

**During work:**

- Commits accumulate against current sprint; prefixed `feat(<stage>):` / `fix(<stage>):`.
- Progress file updated when scope, decisions, blockers, or next steps change materially.
- No updates for trivial incremental work — avoid churn.

### 7.3 Ship

**Trigger:** user runs `/ship`, says "ship it," or similar.

**Steps:**

1. Run sprint-loop quality gate (commands from frontmatter config).
2. Ensure all changes committed.
3. If `version_bump_command` configured, run it.
4. User confirmation before push.
5. Push, monitor CI (if `ci_monitor_command` configured).
6. If CI fails, diagnose root cause, fix, re-push (max 3 attempts, then escalate).
7. Merge to default branch.
8. Create checkpoint tag and backup branch per sprint-loop protocol.
9. Update STATE.md: move Current to Shipped, clear Current section.
10. Require a commit with `ship: <stage>: <summary>` message.
11. Delete the stage's progress file(s).
12. Prompt user: what's the next stage? (Helps pull from Next queue.)

### 7.4 Drift check

**Triggers:** session start, after any commit, on `/where` invocation.

**Logic:** compare STATE.md's Now section against:

- `git branch --show-current`
- `git status --short`
- `git log --oneline -5`

**Mismatch patterns to flag:**

- Current branch differs from STATE.md
- Uncommitted changes on a branch STATE.md describes as parked or shipped
- No progress file exists for the Now sprint
- STATE.md last-updated field is > 3 days old
- Completion plan references stages not appearing in STATE.md Next queue within a reasonable horizon

**Output:** structured mismatch report; skill blocks new work until reconciled OR user explicitly overrides with a warning.

### 7.5 Progress reports

**`/where`** — tactical view:

- Reads STATE.md + git reality
- Produces ~15 line block: branch, effort, blocker, next-up (1-3 bullets), parked count, last shipped, staleness flag, mismatch flag
- Read-only; never writes files

**`/roadmap`** — strategic view:

- Reads PRD + completion plan + STATE.md + git tags + ideas.md count
- Produces ~25 line block: vision, today/version, current phase, active work, blocker, progress table (done/now/next/later), sprints remaining, parked count, ideas parked, notes
- Read-only; never writes files

**Format:** both are markdown, pasteable into email or chat. No styling beyond a fixed set of glyphs (✓, ●, ○, ◆).

### 7.6 Replan

**Trigger:** user runs `/replan`, OR drift check surfaces a scope change the active plan didn't anticipate.

**Steps:**

1. Claude summarizes the reason for replan (user input + evidence).
2. Opens a dialogue with the user to clarify what should change in the PRD.
3. Edits `docs/PRD.md` with changes, appending a timestamped entry to a "Revision Log" section at the bottom.
4. If Phase decomposition changed, regenerates `docs/local/completion-plan-<new-date>.md` and archives the old one in `docs/del/`.
5. Updates STATE.md Next queue to reflect new plan.
6. Does NOT edit the active Current sprint — user decides whether to ship it, abandon it, or update it manually.

---

## 8. Success Measures

| ID | Goal | Success criterion |
|---|---|---|
| PL-G1 | Trustworthy bootstrap | A vibe coder can bootstrap a new project in ≤ 15 minutes of conversation and end up with a usable PRD + completion plan + STATE.md. |
| PL-G2 | Drift is always surfaced | 100% of STATE/git mismatches are flagged on session start before any work proceeds. |
| PL-G3 | Reports are one-command | `/roadmap` and `/where` produce pasteable markdown in under 10 seconds, no hand-editing required. |
| PL-G4 | Portable across stacks | The skill adapts to Python, JavaScript, Go, Rust, etc. projects via the sprint-loop config block alone, no skill edits. |
| PL-G5 | Ship discipline | Every shipped stage has a `ship:` commit AND the progress file is deleted. Zero exceptions. |
| PL-G6 | Bootstrap-to-first-sprint time | From `/bootstrap` invocation to first meaningful commit on Sprint A1: ≤ 30 minutes for a simple project. |

---

## 9. Open Questions (to resolve during v1 build)

1. **Existing projects without a PRD** — how does the skill handle them? Offer reverse-engineering from code + git history, or require manual PRD creation? *Lean: offer both modes during bootstrap; reverse-engineer is best-effort and always requires user approval.*
2. **Maturity scale granularity** — the 3-level default is documented; should the template also include commented-out 5-level rows so users can expand by uncommenting? *Lean: yes.*
3. **Ideas parking lot integration with completion plan** — when a parked idea graduates to a committed stage, does the skill do that automatically or only via `/replan`? *Lean: only via `/replan`; automation here would undermine the discipline.*
4. **Persistent agent memory for the skill** — does the skill itself need a memory dir (like sprint-ship has)? *Lean: yes; mirror trading-system's 4-type taxonomy (user / feedback / project / reference).*
5. **Multi-repo handling** — one repo = one project per user decision, but does the skill need to actively detect and refuse to share state across repos? *Lean: defensive check on session start — if STATE.md references a repo root that doesn't match `git rev-parse --show-toplevel`, flag and refuse.*

---

## 10. Non-Goals (explicit exclusions)

- Team features, assignees, permissions
- Issue tracker sync (GitHub Issues, Jira, Linear, Asana)
- Time tracking or billable-hours integration
- Any kind of Gantt chart, burndown chart, velocity metric, or graphical widget
- Cross-project portfolio views
- Any form of "auto-plan the next sprint by reading the code" — sprints are planned by humans (possibly via dialogue with Claude), never inferred
- A chat-first strategic advisor — this is a discipline layer, not a business partner

---

## 11. Relationship to Other Artifacts

- **Grounded in:** `project_log_study_findings.md` — the audit of trading-system's existing infrastructure.
- **Supersedes:** the original `project_log_production_plan.md` at phase-plan level (revised plan already tracked in task board).
- **Patterns borrowed verbatim from:**
  - `docs/PRD-v2.md` (trading-system) — PRD structure
  - `docs/sprint-loop.md` (trading-system) — sprint loop shape
  - `docs/local/STATE.md` (trading-system) — state file shape
  - `.claude/commands/where.md`, `roadmap.md`, `idea.md` — slash-command behaviors (reimplemented as nested skills)
  - `.claude/agents/sprint-ship.md` — closeout agent structure

---

## 12. Acceptance Criteria for PRD Approval

This PRD is approved when the user:

1. Has read it end-to-end.
2. Has resolved or explicitly deferred every item in §9 (Open Questions).
3. Says "approved" or equivalent — at which point the skill build (Phase 4) begins.

---

*End of PRD v1.0 draft.*
