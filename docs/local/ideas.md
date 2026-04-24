# Ideas — parking lot

> **Big strategic ideas (moonshots) live in [`docs/moonshots.md`](../moonshots.md).** This file is for smaller or tactical ideas that aren't yet moonshot-sized. If an idea here grows into something strategic, promote it to `moonshots.md` and strike it here with a pointer.

**How to read:** This is an append-only list of good ideas that are not on the committed roadmap yet. Nothing here is scheduled. Nothing gets deleted — if an idea turns out to be wrong, mark it `~~struck~~` with a reason rather than removing it, so the thinking is preserved. When an idea graduates to real work, mark it `→ started YYYY-MM-DD (branch: ...)` and add it to STATE.md's Now or Next.

**How to add:** Type `/idea <your idea>` and Claude will append a dated entry here. Or edit this file directly.

**How to review:** Ask Claude to read through and suggest which ideas look ready to promote given current project state.

---

## Ideas

### 2026-04-20 — Sprint 1.5 bundle (~5 days)
Portfolio risk panel + Monte Carlo equity + higher-moment surfacing. Full scope in [`docs/local/temp/serious-analysis-gap-review-2026-04-20.md`](temp/serious-analysis-gap-review-2026-04-20.md).
**Status:** Outside formal PRD-v2 Phase A+B scope. Consider for post-v1.0 or as opportunistic fill between Phase A/B stages.

### 2026-04-21 — Security hardening exercise
Run [`docs/local/temp/gemma-prompt-injection-attack-brief-2026-04-21.md`](temp/gemma-prompt-injection-attack-brief-2026-04-21.md) through GPT-5.4-Cyber, convert findings into `tests/security/test_gemma_injection.py`.
**Status:** Outside formal PRD-v2 Phase A+B scope. Natural fit alongside B2 (explain-only command layer) or B3 (bounded actions).

### 2026-04-23 — ~~Use blockchain to track money movement~~
~~use blockchain to track moneymovement~~
**Status:** struck 2026-04-24. Blockchain's trustless-verification property has no buyer in a single-operator system; existing append-only Postgres + CAS (shipped A2) + stage-audit linkage already delivers most of the integrity guarantee. Better cheaper path for tamper-evident records: hash-chained audit rows + periodic OpenTimestamps anchoring to a public chain.

### 2026-04-24 — Test-failure triage agent (not auto-fix)
Reads a failing test output, classifies root cause (test drift / real regression / infra flake / contract violation), proposes a patch, stops for human approval. NOT auto-fix. Hook-triggered on local test fail or CI fail. Rationale: both 2026-04-24 date-drift failures (test_dashboard_no_exit_narration_flow and test_generate_monitor_no_exit_narration_happy_path) would have been "fixed" the wrong way by a naive auto-fixer (patching the assertion instead of the helper), converting a loud failure into silent drift. A triage agent captures the expensive work (parse + diagnose + propose) while keeping the human gate that catches wrong fixes. Conflicts-check: compatible with acquisition-grade traceability (every proposed patch is an auditable artifact, never silent). Slot in only after Phase A+B ship — A4 drift-guard and the parameter inventory are higher leverage first.
**Status:** uncommitted.
