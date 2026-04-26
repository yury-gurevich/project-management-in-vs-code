# PRD: <Project Name>

**Version:** 0.1 draft
**Date:** <YYYY-MM-DD>
**Owner:** <your name>
**Status:** Draft

---

## 1. Executive Summary

<One paragraph: what this project is, who it's for, why it exists. Written so a reader who has
never heard of it can understand the point in 60 seconds.>

---

## 2. Product Thesis

<2-4 bullets on the core beliefs driving the project. What's broken about the status quo, what
changes if this exists?>

---

## 3. Non-Negotiable Principles

<3-7 principles the project will not compromise on. These act as tiebreakers in design decisions.>

1. …
2. …

---

## 4. Scope

### In scope (v1)

- …

### Out of scope (v1)

- …

### Explicit non-goals (never in scope)

- …

---

## 5. Capabilities / Requirements

<Group functional requirements into named workstreams. Give each requirement a short, stable ID
so it can be referenced in commits and progress reports. Example: AUTH-01, AUTH-02, DATA-01.>

### Workstream: <Name>

- **ABC-01** — <requirement statement>
- **ABC-02** — <requirement statement>

---

## 6. Success Measures

<What does "working" look like? Pick 3-6 measurable goals.>

| ID | Goal | Success criterion |
|---|---|---|
| G1 | … | … |
| G2 | … | … |

---

## 7. Maturity Scale

Pick **one** of the two scales below. The 3-level default is the right choice for most projects;
the 5-level expansion is for projects where "in progress" is too coarse to track meaningfully
(e.g. multi-month projects with many partially-built workstreams). You can switch later — just
re-rate every workstream in §8 against the new scale and note it in the Revision Log.

**Default — 3-level scale** (keep this unless the project clearly needs more granularity):

| Level | Meaning |
|---|---|
| 0 | Not started |
| 1 | In progress |
| 2 | Done |

<!--
**Optional — 5-level scale.** To use it: delete the 3-level table above, then uncomment this
block (remove the surrounding `<!--` and `-->` markers). Re-rate every workstream in §8.

| Level | Meaning |
|---|---|
| 0 | Not started |
| 1 | Prototype — exists but not usable end-to-end |
| 2 | Usable end-to-end but not polished |
| 3 | Polished and tested |
| 4 | Observed and stable in the target environment |
| 5 | Expandable and maintainable by someone other than the author |
-->

---

## 8. Product Progress Snapshot

| Workstream | Current level | What moves it up one level |
|---|---|---|
| <Name> | 0 | … |

---

## 9. Roadmap Phases

Phases define the stage-ID phase letter. Keep phases chunky (weeks to months of work), not small.

- **Phase A — <theme>.** Stages A1, A2, …
- **Phase B — <theme>.** Stages B1, B2, …
- **Phase C — <theme>.** Stages C1, …

---

## 10. Revision Log

Append-only. Every time the PRD is revised via `/replan`, add an entry here with date, reason,
summary of change.

- **<YYYY-MM-DD>** — initial draft.
