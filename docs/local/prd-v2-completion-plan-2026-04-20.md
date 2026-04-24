# PRD v2 Completion Plan — Phase A & B

**Date:** 2026-04-20
**Scope:** Everything required to move PRD-v2 Phases A (Trust Foundation) and B (Quiet Command Layer) to a fully shipped state. Phase C (phone-first) and Phase D (market-pack) are explicitly out of scope here, as are all moonshots.
**Source truth:** `docs/PRD-v2.md`, `docs/local/implementation-plan-2026-04-17.md`, `docs/del/phase1-engineering-tickets-2026-04-17.md` (archived), audit at `docs/local/temp/prd-v2-progress-audit-2026-04-20.md`.
**Exit rule:** When every stage in this document is closed and the exit criteria are green, PRD-v2 is done through Phase B and moonshot work may begin.

> **Status note (2026-04-23):** A1, A2, and B0 are now shipped. Stage B1 is the
> active branch-stage, and A3 is the next queued stage. Use
> `docs/local/STATE.md` for live branch/status; this document remains the
> durable sequencing plan plus stage-level contract.

---

## 0. Next stages (2026-04-20 kickoff snapshot)

Two stages run in parallel as the immediate next work. Everything else in this document waits behind them.

| # | Stage | Track | Why it's next | Pre-written spec |
|---|---|---|---|---|
| 1 | **B0 — Gemma narration MVP** *(cloud-for-now ⚠)* | Phase B | Unblocks every later Gemma stage (B1–B5). Sprint plan already written and model choice validated. | [docs/del/sprint-gemma-narration.md](../del/sprint-gemma-narration.md) (archive pointer — shipped via 34cabd1 / b8fb5c0; includes recovery command for the original full sprint spec). |
| 2 | **A1 — Close remaining reliability traps** | Phase A | The last §10 Phase A items blocking Workstream 1 level 4. No upstream dependency; can proceed immediately. | Write just-in-time at sprint start, following the precedent of the narration sprint doc. Scope is defined in §3 Stage A1 below. |

> **⚠ Cloud-for-now marker:** B0 (and every later Gemma stage B1–B5) uses
> the hosted Google Gemma API via `google.genai` instead of local Ollama,
> as a temporary hardware-driven deviation. The deviation, scope, privacy
> cost, and exit conditions are documented in
> [cloud-gemma-dev-mode.md](cloud-gemma-dev-mode.md). PRD-v2 principles are
> unchanged; only the implementation runtime shifts. Read the runbook
> before starting any Gemma stage.

That handoff has now completed: A1, A2, and B0 are shipped. B1 is active and A3 is next, per `docs/local/STATE.md`.

---

## 1. How to read this document

- Stages are ordered. Later stages depend on earlier ones unless noted.
- Each stage is a branch-sized sprint: scope, concrete acceptance criteria, explicit dependencies.
- Every stage ends with the sprint-loop closeout (`docs/sprint-loop.md`). New dev on feature branches; merge to `main` when the quality gate is green.
- Per-stage specs (the equivalent of `sprint-gemma-narration.md`) should be written just-in-time at the start of each stage, not up front.

## 2. Current state (2026-04-20)

| PRD-v2 §10 requirement | Status | Evidence |
|---|---|---|
| Market-data reliability hardening | Partial | Provenance tracking shipped (`d81e97c`); FinBERT retry still sticky |
| Fail-loud scheduler | **Done** | [scheduler.py:1501-1504](src/trading/pipeline/scheduler.py#L1501-L1504) |
| Scanner/PM/Monitor why-no-action | **Done** | `build_*_diagnostics` + `/api/*/diagnostics` |
| Trade lifecycle narrative | **Done (bounded windows open)** | `/api/trades/narrative` in `dashboard/app.py` |
| Shadow-forecast proof loop + scorecards | Partial | Retraining job exists, first full proof cycle not closed |
| Broker idempotency | Partial | `approval_id` reuse detection; live-stage gaps remain |
| Audited stage transitions | **Done** | `ExecutionStageAudit` + `_record_stage_transition_audit` |
| Gemma command grammar / typed intents / audit | Not started | No `src/trading/gemma/` package |
| Command rehearsal mode | Not started | — |
| Concise evidence-grounded explain | Not started | Narration MVP sprint plan ready but unshipped |
| Dashboard parity for command outcomes | Not started | — |

---

## 3. Phase A — Trust Foundation (remaining stages)

Goal: finish everything PRD §10 Phase A requires so that an investigative operator can answer any "why?" from controlled surfaces, and the system fails loudly when trust would otherwise be damaged.

### Stage A1 — Close the remaining reliability traps

**Why:** `M4` dependency-degradation and `R5` FinBERT retry are the only silent-failure traps §10 Phase A still admits. Without them Workstream 1 cannot move past Level 3.

**Scope:**
- FinBERT retry / recovery: break out of sticky zero-vector mode; surface repeated failures as a dependency incident.
- Finish the dependency-degradation → incident rule for provider chain (Stooq / Yahoo / Finnhub / Edgar): every transition into "degraded" opens or appends to a durable incident with a stable dependency tag.
- Remove any remaining silent warnings in monitor / analyst / scanner paths and convert to structured `issue_code` evidence.

**Acceptance criteria:**
- Forced FinBERT failure recovers on next call without process restart; a test proves it.
- Every provider degradation is reproducible from the incident stream without reading logs.
- Grep for `_logger.warning(` on fallback paths returns zero hits that lack a paired `record_agent_event`.

**Dependency:** none. **Target:** Workstream 1 → level 4.

### Stage A2 — Control-plane safety completion

**Why:** `R3` broker-submit idempotency gaps and `R7` CAS-safe `system_state` writes are the last §10 items on staged execution. Without them `live_manual` / `live_autopilot` cannot be trusted.

**Scope:**
- CAS-safe `system_state` writes: add a version / revision column and reject stale writes; keep transition audit tied to the accepted revision.
- Close broker-submit idempotency gaps for live-adjacent stages: idempotency key is deterministic (approval_id + submission_attempt), dedupe is enforced at submit-time not post-hoc.
- Cross-portfolio same-stock policy enforcement (`S8`).

**Acceptance criteria:**
- Two concurrent writers to `system_state` with the same base revision: one succeeds, one is rejected with a structured error; test proves it.
- Replaying a broker submit with the same key is a no-op at the adapter boundary; test proves it for both paper and live.
- Attempting to open a position in stock X in two portfolios is refused with the policy reason in `AnalystDiagnostic` / PM queue diagnostics.

**Dependency:** A1 is not required, can run in parallel. **Target:** Workstream 2 → level 4.

### Stage A3 — Self-recovery boundary hardening

**Why:** Workstream 4 stays at Level 2 because the watchdog lives in the same process as the scheduler. Per §6.2 / §10 trust work, recovery boundaries must fail loud to an *external* observer.

**Scope:**
- Add a process-external health endpoint (`/healthz`, `/readyz`) that returns the scheduler state, lease state, last successful pipeline run, and dependency health summary.
- Fail-loud signaling: on lease loss, watchdog stall, or scheduler stop, open a critical incident with an actor tag readable by an external process monitor.
- Operator-visible recovery-action surface: the existing `RecoveryAction` table should be exposed as `/api/recovery/actions` with status + requesting actor.

**Acceptance criteria:**
- Killing the control-plane lease externally causes `/readyz` to flip within one heartbeat.
- A runbook step documents how to wire the endpoint into a systemd / supervisord / K8s liveness probe.
- Every scheduler stop is backed by a visible incident with `component="scheduler"` and `outcome="recovery_stop"`.

**Dependency:** none. **Target:** Workstream 4 → level 3.

### Stage A4 — Self-improvement guardrails

**Why:** §6.4 and implementation-plan §3.3 require this to reach Phase B. Without it, Workstream 5 stays at Level 2 and parameter drift remains a hidden risk.

**Scope:**
- Cumulative drift guard (`S1`): reject experiment promotions when cumulative parameter delta from baseline exceeds a configurable bound.
- Forbidden parameter pairs (`S2`): declarative rule set; violated pairs block acceptance.
- Experiment finalization thresholds (`S3`): explicit minimum sample count and confidence floor for promotion.
- Parameter-change approval queue separate from trade approvals (`R8`): own table, own dashboard panel, own audit trail.
- Shadow-ML promotion scorecards (`M5`): weekly rollup of shadow-forecast accuracy, exposed at `/api/shadow/scorecard`.

**Acceptance criteria:**
- Attempting to accept an experiment violating any guardrail is refused at the API with the rule name as the reason.
- Parameter-change queue is reviewable from the dashboard without touching trade approvals.
- Scorecard shows at least one full week of validated shadow-forecast performance before any promotion gate is flipped.

**Dependency:** A1 (need clean dependency signal for the scorecard). **Target:** Workstream 5 → level 3.

### Stage A5 — Evidence surface completion

**Why:** Workstream 3 is at Level 4 but two agents still don't publish "why no action" surfaces, and the trade narrative has no documented evidence window. This stage closes §6.3 fully.

**Scope:**
- Researcher "why no parameter change" diagnostic + `/api/research/diagnostics`.
- Reporter "why no alert" diagnostic + `/api/reporter/diagnostics`.
- Trade narrative evidence-window bound: declare and enforce how far back stitching walks (e.g., to the scan that entered the position).
- First complete shadow-forecast proof cycle (`M0` closure): one end-to-end run with ingest → forecast → actualization → report parity pass.
- **Active Incidents pane** (one dashboard window). Two row types live in it:
  1. **Open incidents** — one row per `Incident` from A1 while it is unresolved. The pipeline-run status widget carries an "N active" annotation that mirrors the open-row count. Each row exposes an `[Explain]` button that invokes the B1 `explain_dependency_incident` narration on demand.
  2. **Recovered incidents (reassurance cards)** — when an incident closes, it transforms into a reassurance card in the same pane rather than disappearing. The card carries the B1-generated reassurance narration and two affordances: `[Dismiss]` (removes this card; card-state persisted per incident ID so it stays dismissed across reloads) and `[Don't show me these again]` (silences all future auto-recovered incidents of this `dependency_tag` for this user; stored as a user preference, reviewable/clearable from settings).
- The dismissal preference is scoped per dependency tag, never globally, so silencing `"finbert"` chatter does not silence a Stooq outage. Silenced tags still populate the internal incident stream — silence is a user-facing surface choice only.
- **Every dismiss / silence / send-to-support click writes its own audit row** (user_id, action, target_incident_id or tag, timestamp). Per PRD-v2 §6.3 acquisition-grade traceability, "user hid X" must be discoverable after the fact, not a silent UI preference. A settings panel lists active silence preferences and lets the user revoke any of them; revocation is itself audited.
- **`[Send to support]` button** on the pane that packages active + recent closed incidents into a formatted email and sends to a configured distributor address. New setting `support_distributor_email`. Most invocations are expected to be auto-triggered by the future MASTER supervisor (moonshots.md #6 Tier 2) rather than pressed by the end-user; the manual button remains as a catch-all. Owner principle: end-users are non-technical, so the escalation path is pull-model, not push.

**Acceptance criteria:**
- All six agents (scanner, analyst, PM, monitor, researcher, reporter) have a diagnostics endpoint with the same shape contract.
- Trade narrative API documents its window and rejects requests outside it with a structured error.
- Shadow-forecast proof-cycle report is stored, linked from the dashboard, and reviewed by the operator.
- Active Incidents pane shows one row per open dependency-degradation `Incident`; the "N active" annotation on the pipeline-run widget matches the open-row count.
- When an incident closes, its row transforms into a reassurance card carrying the B1 narration plus `[Dismiss]` and `[Don't show me these again]` affordances. Dismissal state persists across reloads; the silence preference is scoped per `dependency_tag`.
- Every reassurance narration contains the verbatim integrity-reassurance suffix (safety copy) and declines to speculate on fields not present on the incident record; test proves both.
- Clicking `[Send to support]` with the distributor address configured produces an email bundle containing each open/recent incident's tag, reason, error class, timestamps, recovery method, and correlation IDs in a machine-parseable format; a test proves format stability.

**Dependency:** A4 (scorecards). **Target:** Workstream 3 → level 5.

### Stage A6 — Operator Confidence Ledger

**Why:** §11 item 1. Caps off Phase A by giving the operator a single "is today trustworthy?" surface. Trust is the Phase A deliverable; this is the surface that proves it.

**Scope:**
- Single dashboard panel + `/api/confidence/ledger` that aggregates: market-data health, last successful pipeline run, forced-manual reason (if any), approval backlog size, shadow-proof freshness, open incidents count, recovery-action queue depth.
- Color/state logic is declarative (no thresholds hidden in code): each signal has a named rule.
- Daily snapshot persisted so the ledger is reviewable historically.

**Acceptance criteria:**
- Operator can open one page and answer: "Should I trust today's state?" — without clicking through.
- Each signal links to its evidence surface from stages A1–A5.
- Historical comparison ("how did today's trust compare to last Tuesday?") works from stored snapshots.

**Dependency:** A1 – A5. **Target:** §11 item 1 shipped; Phase A exit criteria green.

### Phase A exit criteria

- All §10 Phase A items show "Done" in §2 of this document.
- §8.2 workstream levels: 1 → 4, 2 → 4, 3 → 5, 4 → 3, 5 → 3.
- Success measures: G1 ≥ 95% silent-failure-free over a 30-day window; G2 = 100% of no-action outcomes answerable from surfaces; G5 = stage-gated / idempotent / reversible / auditable across all live-adjacent paths.
- Confidence Ledger has 14 consecutive "trustworthy" days on real runs.

---

## 4. Phase B — Quiet Command Layer (stages)

Goal: let the operator control the system in human words through a locally-run, bounded command channel with full audit, rehearsal, and dashboard parity, as defined in PRD-v2 §5 and §10 Phase B.

### Stage B0 — Gemma narration MVP (foundation) *(cloud-for-now ⚠)*

**Why:** The narration MVP is both the first §11 item 4 delivery (trade-narrative card prose) and the infrastructure (Gemma client, template registry, validation, grounding, audit table) that every later Gemma stage reuses. The sprint plan is already written.

**Runtime deviation:** during dev mode this stage calls the hosted Google Gemma API (`google.genai` + `gemma-4-31b-it`) instead of local Ollama. See [cloud-gemma-dev-mode.md](cloud-gemma-dev-mode.md) for scope and exit conditions.

**Scope:**
- Reference: `docs/del/sprint-gemma-narration.md` (archive pointer for the shipped sprint; includes recovery instructions for the original full spec used as the B1–B5 template precedent).
- Deliverables: `src/trading/gemma/` package with `cloud_client.py`, `templates.py`, `validation.py`, `narration.py`; new `narrations` and `gemma_call_audits` tables; `/api/diagnostics/{id}/narration` GET+POST; dashboard "Why rejected" panel; unobtrusive "cloud dev mode" indicator wherever Gemma output is shown.

**Acceptance criteria:** the sprint plan's §7 list is the contract for this stage. Do not deviate.

**Dependency:** none (can run in parallel with A1/A2). **Status:** shipped via `34cabd1` / `b8fb5c0`; treat current `main` as the B0 baseline for B1–B5 work.

### Stage B1 — Narration scope expansion

**Why:** The MVP only narrates analyst rejections. §5.1 calls for plain-language explanation across the decision surface; §11 #4 (Trade Narrative Card) depends on multi-event stitching.

**Scope:**
- Add narration templates for: approval outcomes, exit decisions (from monitor `no_exit_diagnostics`), regime-gate transitions, stage transitions, shadow-forecast scorecard summaries, and **dependency incidents** (new `explain_dependency_incident` template — takes a dependency-degradation `Incident` record from A1 and returns a plain-language explanation; powers the `[Explain]` button in the A5 Active Incidents pane).
- **`explain_dependency_incident` tone contract.** The narration is reassuring and explanatory, not technical. It states four things in order, using only fields stored on the `Incident` record (no speculation):
  1. **Acknowledge neutrally.** Frame the event as "a technical incident outside of our control" — not an error, not a failure, not the user's problem.
  2. **Recovery duration.** "…recovered in XX minutes" computed from `opened_at` → `closed_at`. If the incident is still open, phrase as "currently being worked on" without inventing an ETA.
  3. **Operational reassurance.** "Trading activities resumed" (or "are paused while we recover" if open). This comes from the degraded/recovered state, not from a guess.
  4. **Integrity reassurance.** "No data loss or leak has been detected. No wallet updates or any activity related to your portfolio were affected." This phrase is a hard-coded template string, not Gemma-generated — safety-critical copy must not be paraphrased.
  - Grounding check must reject any narration that invents facts not present on the incident record (durations, dependency names, impact claims). The integrity-reassurance sentence is a fixed suffix, asserted verbatim by a template test.
- Each template has its own `template_id`, schema, and grounding rules — reuse the B0 framework, do not fork it.
- Still lazy / on-demand only. No pipeline-time Gemma calls.

**Acceptance criteria:**
- At least six new `template_id` values registered with tests (the five listed above plus `explain_dependency_incident`).
- Every event type with a diagnostic endpoint has a paired narration endpoint, including the A5 incidents pane.
- Grounding check rejects any narration invoking a numeric claim not present in input payload; caught by tests per template.

**Dependency:** B0.

### Stage B2 — Gemma Slice A: explain-only command layer

**Why:** PRD §5.3 GEM-01 through GEM-05 and §5.4 command families `status` + `explain`. This is the first stage that interprets operator utterances rather than fixed event IDs.

**Scope:**
- Command grammar v1 covering only `status` and `explain` intent families.
- Typed intent schemas as Pydantic models (e.g., `StatusIntent`, `ExplainIntent{ subject: str, subject_id?: str }`).
- Parser: Ollama-call + constrained-JSON output mapped into the intent schema; refuse or ask bounded clarification on ambiguity.
- Command audit trail: raw request, parsed intent, validation result, actor, outcome, latency. Reuse `GemmaCallAudit` pattern or new `CommandAudit` table with FK to it.
- Evidence-grounded response builder: every explain response cites the stored decision evidence (analyst diagnostic, PM queue, monitor, trade narrative).
- Auth-gated endpoint `/api/command` accepting text + optional rehearse flag.
- No action-bearing intents in this stage — read-only surface only.

**Acceptance criteria:**
- Ten curated phrasings of "why was X rejected today" map to a single `ExplainIntent`; test proves it.
- Ambiguous input ("explain today") returns a bounded clarification request, not a wrong guess; test proves it.
- Every accepted command persists a durable audit row before response is returned.
- Responses contain only grounded facts; grounding check is enforced as in B0/B1.

**Dependency:** B1 (reuses narration + template framework and evidence surfaces from A5).

### Stage B3 — Gemma Slice B: safe bounded actions

**Why:** PRD §5.3 GEM-06 through GEM-08 and §5.4 families `approve` / `reject` / `modify` / `run` / `mode` / `stage` / `pause` / `resume`. This is the stage where Gemma can change state.

**Scope:**
- Typed intent schemas for each action (e.g., `ApproveIntent{ approval_id: str, reason?: str }`, `ModeIntent{ target: "autopilot"|"manual", reason: str }`).
- Policy parity: every intent is routed through the same service layer as the equivalent dashboard action. No broker-facing code path is reachable through Gemma that is not reachable through the dashboard, and vice versa.
- High-risk intents (`mode`, `stage`, `approve`) require explicit confirmation: second call with a confirmation token produced by the first.
- Dashboard parity: every command outcome (success or refusal) emits the same event types already consumed by the dashboard; test proves the outcomes show up on existing surfaces.
- Refuse any intent Gemma cannot map with ≥ threshold confidence — use rehearsal (B4) on borderline cases.

**Acceptance criteria:**
- GEM-08 property test: pick N dashboard actions at random; the Gemma command producing the same intent passes exactly the same policy checks.
- Confirmation semantics are race-safe (first call returns a token, token expires in ≤ 60 s, is single-use).
- Every action goes through `CommandAudit` with outcome + linked state-transition evidence.

**Dependency:** B2 plus A2 (CAS-safe writes — concurrent actions need them).

### Stage B4 — Command rehearsal mode

**Why:** §11 item 2 and PRD §5.3 GEM-06. "What would happen if I did X?" should always be answerable safely before execution.

**Scope:**
- Every action intent accepts a `rehearse: true` flag.
- In rehearse mode, the intent is validated end-to-end and the would-be side effects are computed, but no state is mutated. The response describes what would have happened and what would have been blocked.
- Dashboard gets a matching "rehearse" toggle on high-risk actions.
- Rehearsals are audited in `CommandAudit` with `outcome="rehearsed"` so retrospective review can tell real from simulated.

**Acceptance criteria:**
- A rehearsal of `mode=autopilot` while in forced-manual reports the forced-manual reason and does not clear it.
- A rehearsal of `approve` on an expired approval is refused with the same reason as a real approve.
- No rehearsal path writes to `positions`, `orders`, `approvals`, or `system_state`.

**Dependency:** B3.

### Stage B5 — Daily Quiet Brief

**Why:** §11 item 3. The phone surface (Phase C) needs a compact daily summary; Phase B must provide the backend so the Phase C work is pure UI. Also reduces notification pressure per §4.2.

**Scope:**
- One compact daily summary, generated on schedule from stored evidence (not live): what ran, what changed, what needs attention, trust index delta.
- Generated by the same Gemma explain path (B2) but invoked from a scheduled job rather than on request.
- Persisted as a first-class narration so it can be reviewed historically.
- Exposed at `/api/brief/daily` with a date parameter.

**Acceptance criteria:**
- Brief is generated before market open each trading day.
- Brief is reproducible: rerunning generation produces structurally identical content from identical stored evidence (text may vary within grounding rules).
- Missing a scheduled generation opens an incident (fail-loud per §6.3).

**Dependency:** B2. Runs in parallel with B3/B4.

### Phase B exit criteria

- All §10 Phase B items Done: grammar v1, typed schemas, audit, rehearsal, explain commands, dashboard parity.
- §8.2 Gemma command layer workstream: level 0 → 3.
- Success measure G4 (Command Safety Rate): ≥ 95% of accepted commands map correctly with 0 unsafe bypasses across a 30-day window.
- Every PRD §5.3 requirement (GEM-01 through GEM-08) has at least one passing test pointing to it.

---

## 5. Suggested sequencing (2026-04-20 baseline)

Current live status has moved past the opening rows below: A1, A2, and B0 are shipped; B1 is active; A3 is next.

A strict gate is "A1+A2 must complete before B3 is merged." Beyond that, stages can be interleaved to keep the project running:

| Week(ish) | Parallel tracks |
|---|---|
| 1–2 | A1 + B0 |
| 3 | A2 + B1 |
| 4 | A3 + B2 |
| 5 | A4 + B3 (B3 waits for A2 merge) |
| 6 | A5 + B4 |
| 7 | A6 + B5 |
| 8 | Soak week — confirm exit criteria, 14-day Confidence Ledger run, G1/G2/G4/G5 measurement |

Every merge uses the sprint-loop closeout (`docs/sprint-loop.md`). Stage specs for A1–A6 and B1–B5 should be written just-in-time at the start of each stage, following the precedent set by `sprint-gemma-narration.md`.

## 6. Explicitly out of scope (for this plan)

These belong to later work and must not be started until Phase B is complete:

- PRD-v2 Phase C (phone-first / PWA) — waits for the Confidence-to-Mobile Gate.
- PRD-v2 Phase D (market-pack abstraction) — waits for US loop trust.
- All §11 items except #1 (Confidence Ledger, A6), #2 (Rehearsal, B4), #3 (Quiet Brief, B5), and #4 (Trade Narrative Card, covered by A5 + B1).
- Moonshot #1 (ABIDES distribution), #2 (multi-agent debate), #3, #4 (causal DAG), and Moonshot #5 phase 2 (fine-tuning on system's own reasoning).
- Any Tier 2 / cloud LLM work. Phase B is local-Gemma only.
- Native Android.

## 7. Done condition

PRD-v2 Phase A and B are complete when:

1. All §3 and §4 stages have merged and their acceptance criteria are green.
2. The exit criteria in §3 (Phase A) and §4 (Phase B) are met and confirmed by the Confidence Ledger.
3. A written handoff in `docs/local/progress/` records the exit state and explicitly authorizes starting moonshot work.

Only then does the moonshot track begin.
