# PRD v2 §8.2 Progress Audit

**Date:** 2026-04-20
**Baseline:** PRD-v2 §8.2 snapshot dated 2026-04-17
**Method:** Read `docs/PRD-v2.md` §8.2, then audit each of the 8 workstreams against actual code under `src/trading/` and `tests/`.

---

## Summary

| Workstream | Was | Now | Delta |
|---|---|---|---|
| 1. Core trading runtime | 3 | 3 | stable — two of three silent-failure traps closed |
| 2. Control plane and staged execution | 3 | 3 | stable |
| 3. Operator evidence and explainability | 3 | **4** | +1 — why-no-action surfaces + trade narrative shipped |
| 4. Self-recovery | 2 | 2 | stable |
| 5. Self-improvement | 2 | 2 | stable |
| 6. Gemma command layer | 0 | 0 | stable — no code |
| 7. Phone-first control surface | 0 | 0 | stable — no code |
| 8. Multi-exchange readiness | 1 | 1 | stable |

Only workstream 3 moved up. Workstream 1 saw real progress (scheduler + monitor traps closed) but FinBERT retry/recovery still sticky keeps it at 3.

---

## 1. Core trading runtime — level 3 (unchanged)

**Evidence**
- Silent `MemoryJobStore` fallback removed — jobstore init failure now raises `RuntimeError` at [scheduler.py:1501-1504](src/trading/pipeline/scheduler.py#L1501-L1504) after emitting a structured `jobstore_init_failed` event.
- Monitor `entry_signals_json` decode failure now emits structured `issue_code="invalid_entry_signals_json"` evidence instead of a silent warning at [monitor.py:399-417](src/trading/agents/monitor.py#L399-L417).
- 19 named scheduled jobs with durable `SQLAlchemyJobStore` + replay-for-missed-jobs logic in scheduler.
- Pre-start schema assertion at [scheduler.py:1461-1464](src/trading/pipeline/scheduler.py#L1461-L1464).

**Still missing**
- FinBERT embeddings can stick in zero-vector mode across a process lifetime — retry / recovery semantics not closed.
- Dependency-degradation → incident rule (`M4`) only partially covers provider chain (Stooq / Yahoo / Finnhub).

## 2. Control plane and staged execution — level 3 (unchanged)

**Evidence**
- `ExecutionStageAudit` table records each stage transition with actor / reason.
- Broker adapter protocol with idempotency via `approval_id` reuse detection in `broker.py` and `broker_alpaca.py`.
- Live submission dispatch job + order sync job on scheduler.
- Mode / stage transition validation in `control_plane.py`.

**Still missing**
- CAS-safe `system_state` writes — current SQLAlchemy updates lack explicit version / CAS guards (`R7`).
- Broker-submit retry gates for live-adjacent stages (`R3`).
- Atomic demotion policy not proven; evidence-based readiness criteria absent.

## 3. Operator evidence and explainability — level 3 → 4

**Evidence (all present in code)**
- `build_scanner_diagnostics()` — scanner.py
- `build_analyst_diagnostics()` — analyst.py, surfaced via `/api/analysis/diagnostics`
- `build_pm_queue_diagnostics()` — portfolio_manager.py
- `build_monitor_no_exit_diagnostics()` — monitor.py, with rule names and reason codes
- Trade narrative stitching via `/api/trades/narrative` endpoint in `dashboard/app.py`, backed by stitching logic in `observability/service.py`.

Four of six agents now publish "why no action" diagnostics and a stitched scan-to-exit narrative is available from a controlled surface. This crosses from "trustworthy under scrutiny" (3) to "controlled autonomy" (4): an operator can reconstruct any non-action without reading logs.

**Still missing to reach 5**
- Researcher "why no parameter change" surface.
- Reporter "why no alert" surface.
- Explicit narrative-evidence window bound (how far back the stitching fetches).

## 4. Self-recovery — level 2 (unchanged)

**Evidence**
- In-process watchdog thread in `ObservabilityRuntime` detects `health_controller` heartbeat stall and opens a critical incident.
- Incident and recovery action tables, control-plane lease renewal with leadership-loss detection, dependency probes.

**Still missing**
- Process-external watchdog (systemd / K8s liveness / external monitor) — the current watchdog is in the same Python process and same Postgres as the scheduler.
- Fail-loud alerting on recovery boundary crossings (scheduler stop on lease loss is silent to any external observer).

## 5. Self-improvement — level 2 (unchanged)

**Evidence**
- `ImprovementExperiment` table + `ResearchLog.parameter_changes_json` persistence.
- Regime override mechanism with expiration, config version tracking, shadow-forecast retraining job.

**Still missing**
- Cumulative drift guardrail (`S1`), forbidden parameter-pair rules (`S2`), experiment finalization thresholds (`S3`).
- Parameter-change approval queue separate from trade approvals (`R8`).
- Operator-visible promotion scorecards.

## 6. Gemma command layer — level 0 (unchanged)

**Evidence**: none. No command grammar, typed intent schema, audit trail, or parsing layer. No `gemma`, `commands`, or `intents` module.

**To reach level 1**: command grammar v1 (`status`, `explain`), typed `Intent` schemas, command audit trail table.

## 7. Phone-first control surface — level 0 (unchanged)

**Evidence**: desktop FastAPI dashboard with ~65 endpoints; no mobile layer, PWA, responsive redesign, or native app.

**To reach level 1**: mobile-friendly / PWA shell with safe approval flow and compact status view.

## 8. Multi-exchange readiness — level 1 (unchanged)

**Evidence**
- S&P 500 universe fetch (`services/sp500.py`), `exchange_calendars` library, NYSE trading-day check, Stooq / Finnhub / Edgar providers, broker adapter protocol.

**Still missing**
- Market-pack abstraction (universe / calendar / provider / policy).
- Exchange calendar abstraction — currently hardcoded NYSE.
- Provider mapping and risk policy per market pack.
- Readiness checklist for new-pack approval.

---

## Success-measure status

| ID | Goal | Status |
|---|---|---|
| G1 | Trustworthy autonomy (≥95% silent-failure-free) | Partial — scheduler + monitor traps closed, FinBERT retry still open |
| G2 | Explainable silence (100% no-action answerable from surfaces) | Materially achieved for scanner / analyst / PM / monitor; researcher + reporter gaps remain |
| G3 | Quiet operations (≤20% days need intervention) | Not measurable yet — no daily intervention metric published |
| G4 | Safe command control (≥95% accepted commands correct) | Blocked — Gemma layer not built |
| G5 | Controlled execution readiness (stage-gated / idempotent / reversible / auditable) | Partial — transition audit present, CAS + full idempotency open |
| G6 | Expansion readiness (new market pack with no core rewrite) | Blocked — market-pack boundary not defined |

---

## Next-step recommendations (not a plan — for the operator to sequence)

1. Close the FinBERT retry / recovery trap and finish the dependency-degradation incident rule to cleanly take Workstream 1 to level 4.
2. Add CAS-safe `system_state` writes and complete broker-submit idempotency to take Workstream 2 to level 4.
3. Consider a small Researcher + Reporter diagnostics pass to lock Workstream 3 at 4 and keep it on a path to 5.
4. Self-recovery (Workstream 4) deserves a minimal external health-check endpoint before any phone-first work begins — recovery boundaries should page someone.
5. Gemma and phone-first remain greenfield; per PRD §10 they should follow the trust fixes, not precede them.
