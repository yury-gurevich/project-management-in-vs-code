---
name: idea
description: >
  Use this skill when the user runs /idea, or says something like "idea: X", "parking lot: X",
  "note for later: X", "shelve this: X", "put this on a list: X", or similar. Appends the idea
  to docs/local/ideas.md with a timestamp. Keeps STATE.md's Next queue focused on things actually
  planned — ideas are captured here instead. Does NOT modify STATE.md or the PRD.
---

# /idea — parking lot capture

Append an uncommitted idea to `docs/local/ideas.md` so it doesn't pollute STATE.md's Next queue.

## What to do

1. If `docs/local/ideas.md` doesn't exist, create it with this header:
   ```
   # Ideas Parking Lot

   Uncommitted ideas. Nothing here is scheduled until it's been through /replan and landed in the
   completion plan. Append-only; prune manually when an idea graduates or is dismissed.

   ```
2. Append an entry in the form:
   ```
   - **<YYYY-MM-DD>** — <idea in one sentence>
     - <optional 1–3 supporting lines: context, why now, who it's for>
   ```
3. Confirm to the user with a one-line acknowledgement: `parked: <YYYY-MM-DD> — <idea>`.

## Principles

- **Never edit STATE.md or PRD.** If the user asks to "add this to the plan," push back: ideas are parked; committing them is `/replan`.
- **No prioritization.** Don't re-order or categorize entries. Chronological only.
- **Pruning is manual.** Never delete or archive entries without explicit user direction.
