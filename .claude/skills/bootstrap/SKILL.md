---
name: bootstrap
description: >
  Use this skill when the user runs /bootstrap, or when a session opens on a repo that has no
  docs/PRD.md and the user wants to start a project, or when the user says "set up a new project",
  "initialize project-log", "scaffold a plan", "let's start a project", "from scratch",
  "I have an existing repo, set up project-log", "reverse-engineer a PRD", "generate a PRD from
  this code", "add project-log to this codebase", or similar. Runs the conversational PRD intake
  with three pre-flight branches: (1) PRD already exists → ask replace/replan/leave; (2) no PRD
  on a trivial repo → fresh-start interview; (3) no PRD on a non-trivial repo (≥5 commits OR ≥10
  files OR README ≥500 chars) → offer reverse-engineer mode that drafts a best-effort PRD from
  code + git history (never auto-saves) before falling through to interview-and-write. Drafts
  docs/PRD.md from the template, seeds docs/local/STATE.md with the first stage, creates
  docs/sprint-loop.md, docs/local/project-log.md, and installs a project-level CLAUDE.md. Does
  NOT write source code — this is planning intake only.
---

# /bootstrap — conversational PRD intake + scaffold

Bootstrap a new project by interviewing the user and generating the planning scaffold. Writes
plan files only — never source code.

## Pre-flight check

Three branches based on what's in the repo:

### Branch 1 — PRD already exists

If `docs/PRD.md` already exists, stop and ask:
"A PRD already exists at `docs/PRD.md`. Do you want to (a) replace it — destructive, (b) run
`/replan` to revise it, or (c) leave it alone?"

If the user picks (a), confirm again before overwriting. If (b), hand off to `/replan`. If (c), stop.

### Branch 2 — No PRD, trivial repo

If `docs/PRD.md` is missing AND the repo is **trivial** (all of: < 5 commits on the default branch
AND ≤ 10 source files AND no `README.md` or README < 500 chars), proceed straight to the
fresh-start interview below. This is the greenfield case the skill was originally written for.

### Branch 3 — No PRD, non-trivial repo

If `docs/PRD.md` is missing AND the repo is **non-trivial** (any of: ≥ 5 commits OR ≥ 10 source
files OR README ≥ 500 chars), the user is sitting on real work. Don't assume they want to throw
it away. Stop and offer 3 modes:

"This repo already has work in it (commits / files / README). I can either:
(a) **Reverse-engineer** a draft PRD from your code, README, and git history — best-effort,
    you'll review and refine before anything is saved.
(b) **Fresh-start interview** — pretend the existing code isn't there and walk me through your
    vision from scratch (the existing code stays untouched either way).
(c) **Cancel**."

If (a) → run **Reverse-engineer mode** below, then continue with **The interview** to fill gaps,
then **After the interview** to write files.

If (b) → skip to **The interview** as if greenfield.

If (c) → stop.

## Reverse-engineer mode

Used when the user picked Branch 3 option (a). Goal: produce a draft PRD that captures what's
clearly in the code, leaves explicit `?` markers where intent is unclear, and **never auto-saves
without user approval**.

### Survey the repo

Run, in this order:

```
git log --oneline -50
git log --stat --shortstat --since='6 months ago'
git ls-tree -r HEAD --name-only | head -100
git tag --list
```

Read these files if present (top-level only — don't recurse into deps):

- `README.md` (any case)
- Language manifest: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, `*.csproj`, etc.
- Top-level `docs/` directory listing (don't read every file — a glance at filenames)
- `LICENSE`
- `.gitignore` (a hint at what's tracked vs not)

### Synthesize the draft

Draft a PRD covering all standard sections (executive summary, principles, scope, capabilities,
success measures, maturity scale, roadmap phases, open questions). Specifically:

- **Executive summary**: 1 paragraph inferred from README + manifest description. If README is
  thin, lead with the inferred answer + a `[?]` marker noting what's uncertain.
- **Principles**: extract any explicit "we don't do X" or "always Y" statements from README/code
  comments. List as inferred. Flag inferred ones with `[inferred — confirm]`.
- **Capabilities / requirements**: group by major top-level directory. Give each a tentative ID
  (e.g. `<DIRNAME>-01`). State the capability as you understand it from filenames + README.
- **Success measures**: leave mostly as `[? — ask the user]` unless the README has explicit ones.
- **Maturity scale**: default 3-level. Don't infer levels from code state — too speculative.
- **Roadmap phases**:
  - **Phase A — Stabilize what's here.** Stages A1..An for the obvious near-term work
    (open issues if present, README-mentioned TODOs, missing tests, etc.). Best guess.
  - **Phase B — [? — ask the user about future intent]**.
  - **Phase C+** left empty.
- **Open Questions section**: **at least 3 entries**. Always include:
  1. "Did I get the executive summary right?"
  2. "Are there capabilities I missed or mislabeled?"
  3. "What's the actual next priority — does Phase A match your intent?"
  Plus any inferences you're least confident about.

### Present and validate

Show the draft to the user with explicit framing:

> "This is a best-effort draft from your code, README, and git log. **Nothing is saved yet.**
> Read it through, then we'll do a short interview to fix what I got wrong and fill in the gaps."

Then run **The interview** below — but skip questions whose answers are already obvious in the
draft, and add follow-ups for the inferences flagged `[?]` or `[inferred — confirm]`.

### Approval gate

Do **not** write `docs/PRD.md` until the user explicitly says "approved" / "save it" / "looks
good, save". If they say "let me edit it first", paste the current draft into a code block so
they can edit-then-paste-back. Loop until approved.

Once approved, proceed to **After the interview** below to write all the scaffold files.

### Project-log behavior on reverse-engineer

The first project-log entry is still a single bootstrap line — **do not invent past stages**.
Pre-existing work stays in git history; the project-log starts now. Write:

```
<YYYY-MM-DDThh:mmZ>  —   bootstrap  project-log scaffold initialized — pre-existing code lives in git history (see git log)
```

Phase A starts with this bootstrap. Don't backfill `started`/`shipped` entries for past commits —
that would be dishonest about when the discipline began.

## The interview

Ask these questions conversationally — not as a form, not all at once. Follow up on each answer
before moving to the next. Keep it natural.

1. **What are you building, in one sentence?** Follow up until the description is concrete enough
   that someone unfamiliar with the project would understand the point.
2. **Who is it for?** Solo use / a few friends / the public / a client. The answer shapes
   non-goals and scope.
3. **What does "working" look like?** Pull 3–6 measurable success criteria. Push back on vague
   ones ("feels fast", "looks nice") until they become concrete.
4. **What are the non-negotiable principles?** Things the project will not compromise on.
   3–7 items.
5. **What's the stack?** Language, main libraries, any infrastructure. This shapes `sprint-loop.md`
   frontmatter.
6. **What's the first thing that would prove the idea works?** This becomes Phase A, Stage A1.
7. **What are the obvious non-goals?** Things people might assume you're doing but you explicitly
   aren't.

## After the interview

1. **Summarize back to the user.** Read back your understanding in ~10 lines. Ask for corrections.
   Loop until they say "yes, that's right."
2. **Draft `docs/PRD.md`** from `../project-log/templates/PRD.md`. Fill every placeholder. Use the mandatory
   3-level maturity scale by default. Use Phases A, B, C for the roadmap.
3. **Draft `docs/local/completion-plan-<today>.md`** from `../project-log/templates/completion-plan.md`.
   Decompose Phase A into stages A1, A2, A3 (aim for 3–6 stages in Phase A).
4. **Create `docs/sprint-loop.md`** from `../project-log/templates/sprint-loop.md`. Fill in the quality-gate
   commands for the user's stack. If unsure, leave the command as `"<fill in>"` with a comment.
5. **Create `docs/local/project-log.md`** from `../project-log/templates/project-log.md`. Append
   the first entry below the `## Log` header:
   ```
   <YYYY-MM-DDThh:mmZ>  —   bootstrap  project initialized from PRD v1
   ```
   (No stage yet — bootstrap precedes A1; the dash is fine in the stage column for this one entry.)
6. **Create `docs/local/STATE.md`** from `../project-log/templates/STATE.md`. Seed Now with stage A1.
   Fill the **Repo root** header field with the output of `git rev-parse --show-toplevel`
   (forward slashes, no trailing slash). This is the multi-repo defensive check value — it lets
   session-start refuse to operate when STATE.md is mistakenly read from a different repo's
   `docs/local/`.
7. **Create `CLAUDE.md`** at the repo root from `../project-log/templates/CLAUDE.md`.
8. **Create `docs/local/.gitignore`-ready structure:** ensure `docs/local/` is in the repo's
   `.gitignore`. Add a line if missing.
9. **Report** to the user: one line per file created, plus a "next step" line:
   `next step: open a Claude session, say "start A1", and begin your first sprint.`

## Principles

- **No code.** This skill creates plan files only.
- **Interview, don't form-fill.** Natural conversation. Follow up on unclear answers.
- **Honest about gaps.** If the user can't answer something ("I don't know what my success
  criteria are"), capture that verbatim in the PRD rather than inventing.
- **Idempotency-safe.** Re-running /bootstrap on a bootstrapped repo should detect it and hand
  off to /replan.
- **Reverse-engineer is best-effort, never silent.** Drafts always get an explicit "nothing is
  saved yet" framing, ≥ 3 Open Questions, and an explicit approval gate before writing.
- **Don't invent the past.** When reverse-engineering an existing repo, the project-log starts
  at bootstrap. Pre-existing work lives in git history — never fabricate retroactive
  `started`/`shipped` entries to make the project-log look fuller than it is.
