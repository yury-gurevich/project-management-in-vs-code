# STATE

**Last updated:** <YYYY-MM-DD HH:MM> (by Claude)
**How to read:** this file is a **derived snapshot** of "what is active right now," regenerated
by `/where` from `docs/local/project-log.md` (canonical history) plus the active per-effort
progress file (resume cursor). The Now and Shipped sections will be overwritten on the next
`/where` or `/ship`; hand-edit only if you intend to override the derived view temporarily.
The Next, Parked, and Pointers sections are user-maintained.

---

## Now

- **Stage:** <e.g. A3>
- **Branch:** <feat/a3-...-YYYY-MM-DD>
- **Goal:** <one line — what this sprint delivers>
- **Status:** <one line — exactly where the work is>
- **Blocker / next step:** <one line>
- **Progress file:** `docs/local/progress/<hash>-<date>-<stage>-<slug>.md`

---

## Next

Queued stages (pointers to completion plan):

- **<stage>** — <one line>
- **<stage>** — <one line>

---

## Parked

Branches kept but not active. Each entry: branch, reason, decision date.

- _(none)_

---

## Shipped this month

- **<YYYY-MM-DD> — <stage> — <summary>** — <tag: checkpoint-YYYYMMDD-slug>, commit <sha>

---

## Pointers

Durable references (don't change often):

- **PRD:** `docs/PRD.md`
- **Completion plan:** `docs/local/completion-plan-<YYYY-MM-DD>.md`
- **Project log (canonical history):** `docs/local/project-log.md`
- **Sprint loop:** `docs/sprint-loop.md`
- **Ideas parking lot:** `docs/local/ideas.md`
- **Runbooks:** `docs/local/` (gitignored)
