# Project State

**Last updated:** 2026-04-24 by Claude (B1 merged to main; A3 self-recovery boundary now active)
**How to read:** *Now* = what's being worked on today. *Next* = queued, not started. *Parked* = branch exists but not active; pick up later. *Shipped* = merged to main this month.

Claude updates this file at every state transition (branch start, merge, park, ship). If this file looks stale, ask Claude "/where" and confirm reality.

---

## Now

- **Branch:** `feat/a3-self-recovery-boundary`
- **Goal:** Stage A3 — self-recovery boundary hardening
- **Status:** **In flight, working tree clean.** Five commits landed: fail-loud A3 lease loss (`b8fdaa1`), readiness probe runbook (`721e1bc`), incident actor details (`72198a6`), readiness probe payload hardening (`0b9e121`), control-plane recovery after lease reacquire (`1feafef`). Progress notes in `docs/local/progress/` cover lease-loss stop, probe runtime validation, and readiness recovery actions.
- **Blocker / next step:** Run sprint-loop quality gate, then PR/merge to `main`.

## Next

- **A4 Self-improvement guardrails** — see `docs/local/prd-v2-completion-plan-2026-04-20.md` §3 Stage A4. Drift detection on scorecards, parameter-change guardrails, Workstream 5 → level 4.
  - **Kick-off deliverable:** T0/T1/T2 tunable-parameter inventory (invariant / operator-tunable / self-tunable) as a precondition for the drift guard (S1) and forbidden-pair rules (S2). Also de-duplicate literals that shadow existing Config table columns.

> Only items the completion plan has sequenced, or something you've committed to starting next, go here. Uncommitted good ideas live in [`docs/local/ideas.md`](ideas.md) — use `/idea` to capture one quickly.

## Parked

- **`fix/recommendation-distribution-fk-2026-04-21`** — merged forward into `main`; keep until CI run `24715710993` is fully green and cleanup is done.
- **`feat/postgresql-migration`** — earlier branch for Postgres/Alembic migration. May be superseded by current fix branch; confirm before deleting.
- **`feature/ml-1-signal-accuracy-predictor`** — shipped in v0.5.1; keep until next cleanup sweep.
- **`feature/ml-2-adaptive-weight-optimizer`** — shipped in v0.5.1; keep until next cleanup sweep.
- **`feat/ml3-ensemble`** / **`feat/ml4-news-impact`** / **`feat/ml5-exit-timing`** — shipped 2026-04-09 in v0.6.0 / v0.7.0 / v0.8.0; keep until next cleanup sweep.
- **`feat/gemma-narration-mvp`** — merged to main via b8fb5c0; safe to delete.
- **`backup/main-after-20260421-recommendation-fk-azure-postgres`** — backup point for the shipped FK/Azure Postgres work; keep for one sprint.
- **`backup/main-after-20260421-hosted-gemma-ci-hotfix`** — backup point; keep for one sprint.

## Shipped this month (2026-04)

- **Stage B1 — Narration scope expansion** (`feat/b1-narration-scope-expansion`, `5258b3d` — 2026-04-23) — merged to `main`. Narration now covers analyst rejections, regime-gate diagnostics, dependency incidents, monitor no-exit diagnostics, exit decisions, stage transitions, approval outcomes, and shadow-scorecard summaries. Gemma dispatcher + template registry + dashboard expose on-demand Explain surfaces for every slice; 114-test targeted verification passed.
- **Stage A2 — Control-plane safety completion** (`feat/a2-control-plane-safety`, PR #8, v0.10.0 — 2026-04-23) — merged to `main` after adding control-plane CAS revision enforcement, stage-audit revision linkage, explicit approval resubmission flow with attempt-scoped broker idempotency, cross-portfolio same-stock rejection, and review/CI follow-up fixes.
- **Stage A1 — Close remaining reliability traps** (`feat/a1-reliability-traps`, `1952414`, v0.9.0 — 2026-04-23) — all silent fallback `_logger.warning()` paths now emit `record_agent_event()` structured evidence across scanner, monitor, FinBERT, news-embeddings, Stooq, Finnhub, Edgar. 10 new event types, 1167 tests passing.
- **Gemma narration MVP** (b8fb5c0, 34cabd1) — on-demand narration for analyst diagnostics with template registry, JSON schema validation, numeric grounding check, GemmaCallAudit, Narration table.
- **ABIDES distributions + hosted Gemma dev mode** (0b95d32) — ABIDES-derived distributions integrated into the pipeline; hosted Gemma usable as dev fallback.
- **Hosted Gemma CI hotfix** (26c6cb9) — restored quality gates.
- **ML-5 Exit Timing Optimizer** (49d0520, v0.8.0 — 2026-04-09) — latest shipped version.
- **ML-4 News Impact Predictor** (616a40f, v0.7.0 — 2026-04-09).
- **ML-3 Ensemble Meta-Learner** (13c2abb, v0.6.0 — 2026-04-09) — Optuna hyperparam search + SHAP attribution.
- **Observability recovery + dashboard alerts** (ef4e64a) — checkpoint.

---

## Pointers (durable references)

**Product direction & scope**
- Product PRD: [`docs/PRD-v2.md`](../PRD-v2.md)
- Moonshots: [`docs/moonshots.md`](../moonshots.md)
- Forward vision & roadmap: [`docs/future/`](../future/) (start at `README.md`)

**Execution**
- Active Phase A/B completion plan: [`docs/local/prd-v2-completion-plan-2026-04-20.md`](prd-v2-completion-plan-2026-04-20.md)
- Implementation order: [`docs/local/implementation-plan-2026-04-17.md`](implementation-plan-2026-04-17.md)
- Sprint workflow: [`docs/sprint-loop.md`](../sprint-loop.md)

**Runbooks**
- Analyst diagnostics: [`docs/local/analyst-runbook.md`](analyst-runbook.md)
- Shadow-forecast smoke: [`docs/local/shadow-forecast-smoke-runbook.md`](shadow-forecast-smoke-runbook.md)
- Cloud Gemma dev-mode deviation: [`docs/local/cloud-gemma-dev-mode.md`](cloud-gemma-dev-mode.md)

**Folders**
- Active progress reports: `docs/local/progress/` (hash-prefixed; delete when shipped)
- Scratch / temp notes: `docs/local/temp/` (emptied at sprint closeout)
- Archived docs: `docs/del/` (shipped or superseded; reversible with `mv`)
