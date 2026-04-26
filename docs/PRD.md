# PRD: `project-log` Skill

**Version:** 1.1 (skill package v0.3)
**Date:** 2026-04-26
**Status:** Approved — Phase C (v1.0 readiness) in progress
**Owner:** Yury Gurevich
**Grounded in:** `project_log_study_findings.md` (2026-04-24)
**Revision Log:** see §13.

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
2. **Single source of truth per tier.** PRD for vision, completion plan for ordering, project-log + per-effort progress for chronology, STATE.md for the current human-readable snapshot derived from those.
3. **Mapping tokens everywhere.** Every sprint, branch, progress file, log entry, and commit carries the stage ID linking it back to the PRD.
4. **Append-only logs; per-effort files distil to milestones on ship.** The per-effort progress file is the append-only sprint log — its tail is by definition where the agent left off. On ship, its key beats are distilled into a one-line milestone in the lifetime project-log, and the per-effort file is then deleted. The project-log is never edited or pruned; it is the durable narrative.
5. **Drift check is mandatory.** At session start and at every state transition, the skill reconciles STATE.md against git reality and against the project-log tail.
6. **The tool is dumb; the plan is smart.** Slice size, commit cadence, and ship criteria live in the active sprint plan, not hardcoded in the skill.
7. **Intake is conversational, not automated.** Bootstrap is a dialogue with Claude, not a wizard. The skill packages the prompts and the scaffold templates, but the judgment lives in the conversation.
8. **Auto-trigger over slash-typing.** Every skill is described so Claude picks it up from natural phrasing — "where are we", "I just shipped", "I'm blocked on X". Slash commands stay as fast-path shortcuts, not the primary surface. The user should not have to remember which skill to invoke.
9. **The coding agent owns milestone capture.** Every meaningful state transition (started / shipped / decision / blocker / unblock / scope change) is written to the project-log by the agent at the moment it happens — not retrospectively, not by the user.

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

### 5.1 Plan hierarchy

| Tier | Artifact | Purpose | Location | Lifecycle |
|---|---|---|---|---|
| 1 | Overarching plan | Vision, principles, requirements, success measures, **maturity scale**, roadmap phases | `docs/PRD.md` | Tracked in git. Rarely rewritten. Evolves via explicit `/replan`. |
| 2 | Completion plan | Ordered decomposition of PRD into stages labeled `[PHASE][N]` | `docs/local/completion-plan-<YYYY-MM-DD>.md` | Gitignored. Evolves with each phase. Replaced (not edited) on major direction shifts. |
| 3a | **Project-log (lifetime)** | Append-only chronological record of milestones across the project's life. Written by the coding agent at every meaningful transition. | `docs/local/project-log.md` | Gitignored. **Never edited, never pruned.** Survives every ship. |
| 3b | **Per-effort progress (transient)** | Append-only sprint log capturing detail during one stage. Its tail is the agent's resume cursor. | `docs/local/progress/<hash>-<YYYY-MM-DD>-<stage>-<slug>.md` | Gitignored. Distilled into one project-log line on ship, then deleted. |
| 3c | STATE.md (derived snapshot) | Human-readable "where are we now" view. Auto-regenerated from project-log tail + active progress-file tail by `/where`. | `docs/local/STATE.md` | Gitignored. Treated as a derived view; rarely hand-edited. |

### 5.2 Stage-ID convention

- **Format:** `[PHASE][N]` — single uppercase letter A/B/C/..., then small integer.
- Phase letters come from PRD roadmap Phases (Phase A, Phase B, etc.).
- Integer orders stages within a phase.
- Examples: `A1`, `A3`, `B1`, `C2`.

Stage IDs propagate into:

- **Branch names:** `feat/<stage>-<YYYY-MM-DD>`, `fix/<stage>-<YYYY-MM-DD>`
- **Progress file names:** `<hash>-<YYYY-MM-DD>-<stage>-<slug>.md`
- **Commit messages:** `feat(<stage>): <summary>`, `fix(<stage>): <summary>`, `ship: <stage>: <summary>`
- **Project-log entries:** every line carries the stage ID as a column.

### 5.3 Project-log entry format

Each line of `docs/local/project-log.md` is a single self-contained record. Format:

```
<ISO-8601 timestamp>  <stage>  <kind>  <one-line description>  [→ <pointer>]
```

Where `<kind>` is one of: `started`, `shipped`, `decision`, `blocker`, `unblock`, `replan`, `parked`, `note`. The optional pointer is a checkpoint tag, commit sha, branch name, or progress-file path — whatever the most useful breadcrumb is for that kind.

Examples:

```
2026-04-25T14:20Z  A4  started   branch feat/a4-self-improvement-guardrails-2026-04-24
2026-04-25T16:10Z  A4  decision  route AutoResearch through parameter_change_queue, not auto-apply
2026-04-25T18:05Z  A4  blocker   CI run 24921142480 cancelled — version bump superseded
2026-04-25T19:00Z  A4  unblock   CI green on retry — run 24921797794
2026-04-25T19:45Z  A4  shipped   guardrails landed  → checkpoint-20260425-a4-self-improvement-guardrails
```

This format is grep-friendly, tail-friendly, and trivially summarizable by `/roadmap` and `/where`.

### 5.4 Resume cursor — tail-of-file convention

The agent's resume point is **the last entry of the active per-effort progress file**, not a separate marker. Append-only is enforced as a discipline; new content goes at the bottom; the bottom is by definition "where we left off." When `/where` runs, it tails the active progress file and reads the most recent entry's "Next" line. No separate cursor file, no resume marker comment, no race conditions.

If a session ends mid-thought without a clean "Next" line, that is itself a useful signal: `/where` will surface "no clean cursor — last entry truncated" and the agent or user states the next step before resuming.

### 5.5 STATE.md structure (derived view)

STATE.md is now a derived snapshot that `/where` regenerates from the project-log tail and the active per-effort progress file. Users may still hand-edit it if they want, but the canonical truth lives in the logs. Fixed sections (in order):

1. **Header** — last updated (by Claude), brief "how to read" note
2. **Now** — current branch, goal, status, blocker / next step (sourced from latest project-log `started` / `blocker` / `unblock` entries + tail of active progress file)
3. **Next** — queued stages with pointers to completion plan
4. **Parked** — branches kept but not active, with reason
5. **Shipped this month** — recent merges with stage / commit / version info (sourced from project-log `shipped` entries within the last 30 days)
6. **Pointers** — durable references (PRD, completion plan, project-log, sprint-loop, runbooks)

### 5.6 Sprint-loop contract & tool-stack config

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

### 5.7 Maturity scale

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
.claude/skills/
├── project-log/                  main skill — doctrine + session-start behavior
│   ├── SKILL.md                  triggers when the user asks status-type questions
│   ├── README.md                 install instructions
│   └── templates/                shared by the command skills
│       ├── PRD.md                PRD template with maturity scale skeleton
│       ├── completion-plan.md    stage list template
│       ├── STATE.md              state file template (derived view)
│       ├── project-log.md        lifetime milestone log header
│       ├── sprint-loop.md        sprint-loop with config frontmatter
│       ├── progress-report.md    in-flight progress template
│       └── CLAUDE.md             project-level Claude pointer template
├── where/SKILL.md                /where — "you are here" with drift reconciliation
├── roadmap/SKILL.md              /roadmap — one-page strategic view
├── idea/SKILL.md                 /idea — parking-lot capture to ideas.md
├── bootstrap/SKILL.md            /bootstrap — conversational PRD intake + scaffold
├── replan/SKILL.md               /replan — structured PRD revision with change log
├── ship/SKILL.md                 /ship — ship protocol: quality gate, merge, cleanup
└── log/SKILL.md                  /log — milestone writer used by the coding agent
```

### 6.1 Invocation

- **Main SKILL.md** auto-triggers when Claude opens the repo and the skill is installed.
- **Sibling skills** auto-trigger from natural phrasing (per principle 8) and additionally invoke as slash commands (`/where`, `/roadmap`, `/idea`, `/bootstrap`, `/replan`, `/ship`, `/log`).
- Each slash command is a top-level sibling skill, which is what Cowork's skill loader expects — they work consistently across Cowork, Claude Code CLI, and Claude Desktop.
- **Description-driven dispatch.** Every SKILL.md description names the slash command **and** lists the natural-language phrasings that should fire the skill. Claude is expected to pick the right skill from context; the user does not have to remember which slash command does what.

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
6. Claude creates `docs/local/project-log.md` from `templates/project-log.md` and writes the first entry: `<timestamp>  —  bootstrap  project initialized from PRD <vN>`.
7. Claude creates `docs/local/STATE.md` from the template with stage A1 seeded as Now.
8. Claude creates `docs/sprint-loop.md` with a starter frontmatter config (user fills in exact commands for their stack).
9. Claude installs project-level `CLAUDE.md` pointing future Claude sessions to STATE.md + project-log + sprint-loop.
10. Bootstrap complete; first sprint ready to execute.

### 7.2 Sprint execution

**At session start:**

1. Main SKILL.md reads STATE.md and the tail of `docs/local/project-log.md` (last ~20 lines).
2. Reads the active per-effort progress file's tail (last ~30 lines).
3. Runs drift check against git reality (same logic as `/where`).
4. If drift detected, surfaces it and blocks further work until reconciled or explicitly overridden.
5. If no Current sprint defined, prompts user to pick the next stage from Next.
6. Otherwise, the agent reports back: "we left off at: `<tail-of-progress 'Next' line>`" and continues.

**During work:**

- Commits accumulate against current sprint; prefixed `feat(<stage>):` / `fix(<stage>):`.
- Per-effort progress file is appended to (never edited) when scope, decisions, blockers, or next steps change materially. Each append includes a "Next:" line as the last bullet — this is the resume cursor.
- No updates for trivial incremental work — avoid churn.
- **At every milestone, the agent invokes the `log` skill** (or writes the line directly into `docs/local/project-log.md`). Milestones: stage start (branch created), decision, blocker found, blocker resolved, scope change, parked. Ship is logged automatically by `/ship`. See §7.7 for milestone capture details.

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
9. **Distil the per-effort progress file into a project-log entry.** Read the progress file, summarize its arc into one line, and append to `docs/local/project-log.md`: `<timestamp>  <stage>  shipped  <summary>  → <checkpoint-tag>`.
10. Update STATE.md (regenerate Now + Shipped sections from project-log).
11. Require a commit with `ship: <stage>: <summary>` message.
12. Delete the stage's progress file(s) — the project-log entry is now the durable record.
13. Prompt user: what's the next stage? (Helps pull from Next queue.)

### 7.4 Drift check

**Triggers:** session start, after any commit, on `/where` invocation.

**Logic:** compare STATE.md's Now section, project-log tail, and git reality:

- `git branch --show-current`
- `git status --short`
- `git log --oneline -5`
- Tail of `docs/local/project-log.md`

**Mismatch patterns to flag:**

- Current branch differs from latest project-log `started` entry that hasn't been `shipped` yet
- Uncommitted changes on a branch the project-log marks as already shipped
- No progress file exists for the Now sprint, but project-log shows it as still active
- Project-log latest entry is > 3 days old (likely missing milestone capture)
- Completion plan references stages not appearing in STATE.md Next queue within a reasonable horizon
- STATE.md disagrees with project-log tail (regenerate STATE.md and warn the user that hand-edits will be overwritten)

**Output:** structured mismatch report; skill blocks new work until reconciled OR user explicitly overrides with a warning.

### 7.5 Progress reports

**`/where`** — tactical view:

- Reads STATE.md, project-log tail (last ~20 entries), active per-effort progress file tail, git reality
- Regenerates STATE.md's Now section from project-log + progress-file tails (writes if drift found and user approves)
- Produces ~15 line block: branch, effort, blocker, next-up (1-3 bullets — primary source is the progress file's last "Next:" line), parked count, last shipped, staleness flag, mismatch flag
- The only write `/where` ever performs is regenerating STATE.md's Now section after surfacing drift; never writes elsewhere

**`/roadmap`** — strategic view:

- Reads PRD, completion plan, project-log (full), git tags, ideas.md count
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
6. **Appends a `replan` entry to `docs/local/project-log.md`** summarizing the change in one line.
7. Does NOT edit the active Current sprint — user decides whether to ship it, abandon it, or update it manually.

### 7.7 Milestone capture (`/log` and auto-invocation)

**Trigger:** the coding agent recognizes that a milestone has just occurred — or the user explicitly says "log this," "note that I just shipped X," "I'm blocked on Y," or runs `/log`.

**What counts as a milestone (each writes one line):**

- `started` — a new branch is created for a stage (auto-fired by the agent on `git checkout -b feat/<stage>-…`)
- `decision` — a non-obvious technical or product call that future readers should know about
- `blocker` — work cannot progress without external input or upstream resolution
- `unblock` — a previously logged blocker is resolved
- `replan` — written by `/replan` (see §7.6)
- `parked` — a branch is being parked rather than shipped
- `shipped` — written by `/ship` (see §7.3)
- `note` — anything else worth a one-liner; use sparingly to keep signal high

**Steps:**

1. Determine the kind from context (or take it from the user's phrasing).
2. Construct the line in §5.3 format.
3. Append to `docs/local/project-log.md`. Never edit existing entries.
4. Confirm to the user with a one-line acknowledgement: `logged: <stage> <kind> — <summary>`.

**Principles for the agent:**

- **One milestone, one line.** No multi-line entries; if it doesn't fit on one line, it's two milestones or a progress-file note instead of a log entry.
- **At the moment, not retrospectively.** Milestones are written when they happen, not in a batch at session end.
- **Idempotent enough.** Re-firing the same `started` or `shipped` event within a few seconds should not produce a duplicate; the agent checks the tail before appending.

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
| PL-G7 | Auto-trigger reliability | Across the 7 sibling skills, ≥ 90% of "natural-phrasing" invocations fire the right skill without the user typing a slash command. Measured by sampling 20 sessions per release. |
| PL-G8 | Milestone density | Every shipped stage has at least one `started` and one `shipped` entry in `project-log.md`. ≥ 80% of shipped stages also have at least one `decision` or `blocker`/`unblock` entry. |

---

## 9. Open Questions

Resolved in v1.1:

- **Q (was open):** Should the agent's resume cursor be a separate marker, footer comment, or just the tail of the per-effort progress file? **Resolved:** tail-of-file is the cursor. See §5.4.
- **Q (was open):** Should milestones live in STATE.md, in per-effort progress files, or in a separate log? **Resolved:** lifetime `docs/local/project-log.md` for milestones; per-effort progress for sprint detail; STATE.md becomes a derived view.
- **Q (was open):** Is the user expected to invoke skills by slash command? **Resolved:** no — auto-trigger is the primary surface (principle 8). Slash commands are shortcuts.

Resolved in skill package v0.3 (Phase C):

- **Q (was Q2):** Maturity scale granularity — should the template include a commented-out 5-level option? **Resolved (C4, 2026-04-26):** yes. Template now ships the 3-level default plus a commented-out 5-level expansion with explicit "pick one" wording and switch-later instructions. See `templates/PRD.md` §7.

Still open for v1.x:

1. **Existing projects without a PRD** — how does the skill handle them? Offer reverse-engineering from code + git history, or require manual PRD creation? *Lean: offer both modes during bootstrap; reverse-engineer is best-effort and always requires user approval.* (Tracked as C5.)
2. **Ideas parking lot integration with completion plan** — when a parked idea graduates to a committed stage, does the skill do that automatically or only via `/replan`? *Lean: only via `/replan`; automation here would undermine the discipline.*
3. **Persistent agent memory for the skill** — does the skill itself need a memory dir (like sprint-ship has)? *Lean: yes; mirror trading-system's 4-type taxonomy (user / feedback / project / reference).* (Tracked as C2.)
4. **Multi-repo handling** — one repo = one project per user decision, but does the skill need to actively detect and refuse to share state across repos? *Lean: defensive check on session start — if STATE.md references a repo root that doesn't match `git rev-parse --show-toplevel`, flag and refuse.* (Tracked as C3.)
5. **Project-log size** — at what point (file size, line count, or age) does `/roadmap` switch from "summarize the whole log" to "summarize the last N entries"? *Lean: switch at 500 lines or 6 months, whichever comes first; older entries summarized via stage-grouped roll-up.* (Tracked as C6.)
6. **Auto-trigger collisions** — when two skills could plausibly fire on the same phrasing (e.g., "let's plan the next thing" — `/replan` or just generic next-stage selection?), how does the agent disambiguate? *Lean: defer to the most-specific description match; if tied, ask one clarifying question before acting.*

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
  - `.claude/commands/where.md`, `roadmap.md`, `idea.md` — slash-command behaviors (each a top-level sibling skill)
  - `.claude/agents/sprint-ship.md` — closeout agent structure

---

## 12. Acceptance Criteria for PRD Approval

This PRD is approved when the user:

1. Has read it end-to-end.
2. Has resolved or explicitly deferred every item in §9 (Open Questions).
3. Says "approved" or equivalent — at which point the skill build (Phase 4) begins.

---

## 13. Revision Log

- **2026-04-26 — C4 (skill package v0.3).** Closed open question Q2 (maturity scale granularity). PRD template `templates/PRD.md` §7 now ships both scales explicitly: the 3-level default visible, the 5-level expansion in a commented block with "pick one" wording and switch-later instructions. §9 reorganized: Q2 moved to a new "Resolved in skill package v0.3" sub-section; remaining open questions renumbered and cross-referenced to their tracking stages (C2, C3, C5, C6). Reason: dogfood of the skill on its own repo surfaced that the template already had the 5-level option but the PRD said it was open; closing the loop.
- **2026-04-25 — v1.1 (skill package v0.2).** Introduced the lifetime `docs/local/project-log.md` artifact (§5.1, §5.3) and the new `log` sibling skill (§6, §7.7). Defined the tail-of-file resume convention (§5.4). Demoted STATE.md to a derived view regenerated by `/where` (§5.5). Updated principles 2, 4, 5; added principles 8 (auto-trigger over slash-typing) and 9 (coding agent owns milestone capture). Updated Bootstrap (§7.1), Sprint Execution (§7.2), Ship (§7.3), Drift Check (§7.4), Progress Reports (§7.5), Replan (§7.6) to read from / write to project-log. Added success measures PL-G7 (auto-trigger reliability) and PL-G8 (milestone density). Resolved 3 open questions; added 2 new ones (project-log size, auto-trigger collisions). Reason: user feedback that (a) per-effort logging IS the append-target, (b) coding agent must own milestones, (c) skills must auto-trigger from natural phrasing.
- **2026-04-24 — v1.0 draft.** Initial PRD grounded in `project_log_study_findings.md`.

---

*End of PRD v1.1 / project-log v0.3.*
