---
name: replan
description: >
  Use this skill when the user runs /replan, or says "we need to change the plan", "revise the
  PRD", "the direction is shifting", "drop this phase", "add a new workstream", "re-prioritize",
  or similar. Also invoke when /where's drift check surfaces a scope change the active plan
  didn't anticipate. Interviews the user about what's changing, edits docs/PRD.md with a
  Revision Log entry, regenerates the completion plan, and updates STATE.md's Next queue.
  Does NOT edit the Current sprint — that's the user's call.
---

# /replan — structured PRD revision

Guide a structured revision of the PRD and downstream plan files. The revision is always
recorded — no quiet edits.

## What to do

1. **Ask why.** Start with "what's changing and why?" Let the user talk. Summarize back.
2. **Scope the revision.** Is this:
   - A tweak to existing principles or success measures?
   - A phase re-ordering?
   - A new phase or workstream?
   - A scrap-and-restart? (Rare — treat with care.)
3. **Draft the change in-place.** Edit `docs/PRD.md` with the new content. Do NOT remove the old
   version silently — for deletions, move removed sections into a `## Archive` at the bottom of
   the PRD with a timestamped note.
4. **Append to the PRD's Revision Log.** A dated entry, one paragraph:
   ```
   - **<YYYY-MM-DD>** — <summary of change>. Reason: <reason>. Impact: <which phases/stages move>.
   ```
5. **Regenerate the completion plan** if Phase decomposition changed:
   - Archive the current `docs/local/completion-plan-*.md` into `docs/local/archive/` (create if
     needed — gitignored).
   - Create a new `docs/local/completion-plan-<today>.md` reflecting the new plan.
6. **Update `docs/local/STATE.md` Next queue** to match the new plan. Do NOT touch the Now section.
7. **Report** to the user:
   - Which PRD sections changed
   - Completion plan archived + new one created (if applicable)
   - STATE.md Next queue updated
   - Explicit note: "I did not touch the Now sprint. Decide whether to ship it, abandon it, or
     update the progress file manually."

## Principles

- **Every revision is logged.** Revision Log entry is mandatory.
- **Deletions are archived, not dropped.** The PRD grows; it doesn't forget.
- **Never touch Now silently.** The active sprint is under the user's control; `/replan` affects
  what comes after, not what's in flight.
- **One revision at a time.** If the user tries to replan mid-/replan, finish this one and start
  a new invocation.
