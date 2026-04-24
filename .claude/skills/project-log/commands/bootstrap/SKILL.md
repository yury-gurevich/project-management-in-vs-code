---
name: bootstrap
description: >
  Use this skill when the user runs /bootstrap, or when a session opens on a repo that has no
  docs/PRD.md and the user wants to start a project, or when the user says "set up a new project",
  "initialize project-log", "scaffold a plan", "let's start a project", "from scratch", or similar.
  Runs the conversational PRD intake: interviews the user about the idea, drafts docs/PRD.md from
  the template, seeds docs/local/STATE.md with the first stage, creates docs/sprint-loop.md, and
  installs a project-level CLAUDE.md. Does NOT write code — this is planning intake only.
---

# /bootstrap — conversational PRD intake + scaffold

Bootstrap a new project by interviewing the user and generating the planning scaffold. Writes
plan files only — never source code.

## Pre-flight check

1. If `docs/PRD.md` already exists, stop and ask:
   "A PRD already exists at `docs/PRD.md`. Do you want to (a) replace it — destructive, (b) run
   `/replan` to revise it, or (c) leave it alone?"
2. If the user picks (a), confirm again before overwriting. If (b), hand off to `/replan`. If (c), stop.

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
2. **Draft `docs/PRD.md`** from `templates/PRD.md`. Fill every placeholder. Use the mandatory
   3-level maturity scale by default. Use Phases A, B, C for the roadmap.
3. **Draft `docs/local/completion-plan-<today>.md`** from `templates/completion-plan.md`.
   Decompose Phase A into stages A1, A2, A3 (aim for 3–6 stages in Phase A).
4. **Create `docs/sprint-loop.md`** from `templates/sprint-loop.md`. Fill in the quality-gate
   commands for the user's stack. If unsure, leave the command as `"<fill in>"` with a comment.
5. **Create `docs/local/STATE.md`** from `templates/STATE.md`. Seed Now with stage A1.
6. **Create `CLAUDE.md`** at the repo root from `templates/CLAUDE.md`.
7. **Create `docs/local/.gitignore`-ready structure:** ensure `docs/local/` is in the repo's
   `.gitignore`. Add a line if missing.
8. **Report** to the user: one line per file created, plus a "next step" line:
   `next step: open a Claude session, say "start A1", and begin your first sprint.`

## Principles

- **No code.** This skill creates plan files only.
- **Interview, don't form-fill.** Natural conversation. Follow up on unclear answers.
- **Honest about gaps.** If the user can't answer something ("I don't know what my success
  criteria are"), capture that verbatim in the PRD rather than inventing.
- **Idempotency-safe.** Re-running /bootstrap on a bootstrapped repo should detect it and hand
  off to /replan.
