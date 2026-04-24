# PRD v2: Operator-Controlled Single-User Self-Managed Trading Application

**Version:** 2.0 working rewrite
**Date:** 2026-04-17
**Status:** Successor PRD. The original PRD is preserved at `docs/PRD.md`.
**Product Owner:** Yury Gurevich

---

## 1. Executive Summary

This product is not a generic trading assistant. It is a single-user, self-managed stock trading application designed to become the best system in the world for one narrow but demanding job: helping one operator run a disciplined stock-trading process with strong automation, full visibility, local control, and minimal day-to-day friction.

The system must feel quiet, trustworthy, and under control. It should talk to the user as little as possible. It should expose state, decisions, risks, and exceptions through controlled channels rather than through constant conversation.

The product starts with US equities and an S&P 500 universe because trust must be earned on a narrow universe before expanding. The long-term architecture must allow broader US equities, then exchange packs beyond NYSE / Nasdaq / S&P 500, without rewriting the control plane.

The role of Gemma is specific and important. Gemma is not here to be a chatty companion. Gemma exists to run locally as the management, monitoring, explanation, and command-validation layer. It should translate a limited set of human requests into typed, policy-bound actions; explain what the system did in plain language; and refuse anything ambiguous, unsafe, or outside the allowed command set.

The user should have only two meaningful product contact surfaces:

1. **Phone app**: the eventual primary daily interface, introduced late in development after trust is earned.
2. **Dashboard**: the high-visibility forensic and manual-control surface for suspicious, careful, or investigative use.

Everything else is infrastructure, not product surface.

---

## 2. Product Thesis

Build a local-first, single-user trading application that can manage itself conservatively, recover safely, explain itself clearly, and eventually accept well-formed human instructions in everyday language through a tightly controlled command channel.

The product wins if it achieves all of the following at the same time:

- Runs mostly on its own without becoming opaque.
- Makes conservative decisions and exposes why they happened.
- Fails loudly when trust would otherwise be damaged.
- Gives the user only the controls that matter, through bounded surfaces.
- Keeps meaning local: command interpretation, risk policy, and execution validation stay under the operator's control.
- Expands market scope only after the original US-equity control loop is trustworthy.

---

## 3. Non-Negotiable Product Principles

1. **Single-user first.** This is a system for one operator, not a team platform, not a social product, and not a multi-tenant service.
2. **Quiet by default.** The application should not constantly ask questions, narrate itself, or demand attention. Silence is the default state when things are healthy.
3. **Controlled channels only.** User interaction happens through bounded artifacts: approval cards, alerts, summaries, evidence views, and typed commands mapped into approved intents.
4. **Local control of meaning.** Command interpretation, operating mode, execution stage, and decision validation must remain locally controlled, auditable, and reversible.
5. **Evidence before automation.** A capability may operate automatically only after the system can explain it, measure it, and roll it back.
6. **Dashboard is for trust.** The dashboard exists to let an inquisitive or suspicious user inspect the full process, verify decisions, and run manual actions when needed.
7. **Phone is for command and confidence.** The phone app becomes the primary daily surface only after the dashboard proves the process is understandable and trustworthy.
8. **Expansion must be architectural, not ad hoc.** Support for new exchanges or universes must arrive through market-pack abstractions, not code forks.
9. **Cloud is later, not first.** Azure or other cloud services are valid scaling paths after local CPU, memory, or operational limits are reached. Local trust comes first.

---

## 4. Product Surfaces and Contact Model

### 4.1 Primary Product Surfaces

| Surface | Purpose | When it matters | Allowed actions | Must not become |
|---|---|---|---|---|
| Dashboard | Full visibility, forensics, trust building, manual runs, detailed control | Now and always | Inspect every run, inspect every trade, approve/reject/modify, change mode/stage, run diagnostics, read reports | A noisy general chat UI |
| Phone app | Fast daily control surface with concise status and safe commands | Later phase | Approvals, pause/resume, concise explanations, mode toggles, run-safe commands, urgent alerts | A full replacement for deep investigation |

### 4.2 Supporting Transport, Not Additional Surfaces

Notifications are not a third product surface. They are a transport channel whose only purpose is to bring the user back to the dashboard or phone app.

Notification policy:

- Notify for forced manual, approval expiry risk, pipeline failure, severe incident, or stage/policy escalation.
- Do not notify for routine healthy runs.
- Group low-urgency information into scheduled summaries instead of interrupting the user.

### 4.3 Dashboard Requirements

The dashboard must remain the system's truth surface. It must expose:

- full pipeline status and recent run history;
- recommendation evidence and rejection reasons;
- approval queue and execution review;
- position lifecycle and post-trade narrative;
- shadow ML status and scorecards;
- control-plane state (`operating_mode`, `execution_stage`, forced-manual reason);
- incident, recovery, and dependency-health views;
- an **Active Incidents pane** that remains visible whenever any dependency-degradation incident is open; the pipeline-run status widget shows an accompanying "N active" annotation so the operator can never miss the fact that the pipeline produced output while a component was degraded;
- manual run triggers and clear operator-safe recovery actions.

The dashboard must never hide a material decision behind logs alone.

### 4.4 Phone App Requirements

The phone app is a late-phase product surface and should be intentionally narrow.

It must support:

- a compact daily status view;
- pending approvals and urgent exceptions;
- pause / resume / switch-to-manual controls;
- one-step access to "why did this happen" summaries;
- safe command entry in controlled human language;
- bounded report views for confidence-building.

It must not attempt to ship full admin workflows, full observability trees, or development tooling. Those remain in the dashboard.

Mobile delivery order:

1. Secure mobile-friendly dashboard / PWA.
2. Focused phone-first control workflow.
3. Native Android app if the mobile control path proves worthwhile.

---

## 5. Local Gemma Control Agent

### 5.1 Role

Gemma is the local command-and-validation layer for the operator. It exists to make the system easier to control without making it less safe.

Gemma's responsibilities:

- translate approved human-language commands into typed intents;
- produce concise explanations grounded in stored evidence;
- validate intent against policy and current system state;
- refuse or escalate ambiguous or unsafe requests;
- help summarize incidents, stage decisions, and unusual outcomes.

Gemma must operate from structured evidence first, not from improvisation.

### 5.2 Hard Boundaries

Gemma must not:

- invent trades outside the system's policy and data path;
- bypass approval or stage gates;
- submit broker actions directly without the same control-plane checks as every other path;
- mutate strategy parameters outside the approval and audit flow;
- become a free-form, open-ended conversational trading advisor.

### 5.3 Gemma Requirements

- **GEM-01 Local-only command processing.** The primary command and explanation path must run locally.
- **GEM-02 Allowed intent grammar.** Only a defined command set may execute actions.
- **GEM-03 Typed command schema.** Every accepted command must map to a validated schema before execution.
- **GEM-04 Safe failure on ambiguity.** If Gemma cannot confidently map a request to one intent, it must refuse or ask for a bounded clarification.
- **GEM-05 Evidence-grounded explanations.** Explanations must cite stored decision evidence, not speculation.
- **GEM-06 High-risk confirmation.** Mode changes, stage changes, approvals, and manual runs require explicit confirmation semantics.
- **GEM-07 Durable audit.** Every accepted command must generate an audit trail with raw request, parsed intent, validation result, actor, and outcome.
- **GEM-08 Policy parity.** A command issued through Gemma must obey the same rules as one issued from the dashboard.

### 5.4 Initial Allowed Command Families

The first command language should stay small:

- `status` - "show today's status", "why is the system in manual"
- `explain` - "why was AAPL rejected", "why no trades today"
- `approve` / `reject` / `modify` - bounded approval actions
- `run` - manual paper run, diagnostics refresh, report generation
- `mode` - switch between `autopilot` and `manual`
- `stage` - request or confirm allowed stage transitions
- `pause` / `resume` - stop or resume new entries under policy

Anything beyond this must be explicitly added to the command grammar.

---

## 6. Core Product Capability Requirements

### 6.1 Trading Engine and Execution

- Start with US equities and an S&P 500 universe.
- Preserve paper-first foundations and staged promotion through `paper`, `broker_shadow`, `live_manual`, and `live_autopilot`.
- Keep shadow ML advisory until scorecards prove it deserves promotion.
- Support multiple portfolios for a single operator, but keep policy boundaries explicit and auditable.
- Treat recommendation yield and market-data trust as first-class product concerns, not merely implementation details.

### 6.2 Control Plane

- Persist requested and effective `operating_mode` and `execution_stage`.
- Support forced-manual behavior when observability or policy demands it.
- Keep approval lifecycle durable, inspectable, and reversible.
- Ensure broker submission is idempotent before live-adjacent stages become normal.
- Make stage promotion / demotion evidence-based and policy-driven.
- Keep every state transition attributable to a user action, policy action, or recovery action.

### 6.3 Observability and Trust

- Every recommendation must be explainable.
- Every non-action must be explainable: why no recommendation, why no entry, why no exit, why no promotion.
- Every incident and recovery action must be durably visible.
- Every trade must have a stitched narrative from scan to exit.
- Shadow forecasting and other advisory ML must publish operator-facing scorecards before they influence hard decisions.
- The system should prefer concise summaries over raw log exposure, but must allow deeper drill-down in the dashboard.
- **Explain-on-demand pattern.** Every technical artifact surfaced to the user — an incident, a diagnostic, a decision, a rejection reason — carries an `[Explain]` affordance that invokes the local Gemma narration layer to produce a plain-language explanation on demand. High-fidelity internal state stays intact; Gemma does the translation when (and only when) the user asks. This is the standard pattern for bridging *loud-internal / quiet-user-facing* observability without dumbing down the underlying evidence.
- **User-facing voice is reassuring and explanatory, never technical.** When any system event is rendered to the end-user (incident card, recovered-incident card, daily brief, trade-narrative summary), the voice:
  - frames disruptions as "a technical incident outside of our control," not as a failure or the user's problem;
  - states concrete recovery facts (duration, resumption of activity) derived only from stored evidence, never guessed;
  - includes fixed safety-copy reassurance on data integrity and portfolio safety verbatim — safety-critical sentences are hard-coded template strings, not Gemma-generated;
  - offers dismissal affordances (`[Dismiss]` for this event, `[Don't show me these again]` per category) so the user is never trapped holding a notification they cannot act on.
- **Acquisition-grade traceability.** Though this is a hobby project today, the audit surface is built as if it could be acquired tomorrow. A prospective buyer, auditor, or regulator should be able to reconstruct any past state of the system, any past decision, and any past user action without gaps. Concrete rules:
  - **Append-only history.** Incidents, diagnostics, approvals, stage transitions, command audits, narrations, and the forthcoming `CommandAudit` / parameter-change queue are append-only. State transitions (open → closed, pending → approved) are new rows or new fields on the same row, never a destructive overwrite of the event. Deletion is not a supported operation on audit-bearing tables.
  - **User actions are audited, not just persisted.** When the user dismisses a card, silences a dependency tag, clicks `[Send to support]`, confirms a high-risk intent, or accepts a parameter change, the action itself produces a timestamped, user-attributed audit row — not just a mutation of the target object. "User silenced `finbert` reassurance cards on 2026-04-22" must be discoverable after the fact.
  - **Silence does not erase.** Dismissal and silence preferences are UI-layer filters only. The underlying incident, diagnostic, and provenance records persist in full fidelity, independent of what the user chose to hide.
  - **Decision provenance travels.** Every decision record produced during a degraded-dependency window carries a provenance pointer to the open incident (A1 §5.4). An external auditor asking "what data did this reject rely on?" gets a deterministic answer, not a log-scrape.
  - **Exportable bundle.** The audit surface must be exportable as a machine-parseable bundle for any date range (format: stable; fields: declared in a schema, not ad-hoc). The A5 `[Send to support]` email is the first instance of this; the general capability is future work but its feasibility must not be compromised by earlier choices.
  - **No silent retention policy.** Retention windows, if any, are declared in configuration and produce their own audit rows when they trim. A row disappearing without a corresponding "trimmed under policy X at time T" entry is a defect.

### 6.4 Self-Management

- Keep deterministic self-improvement as the first layer.
- Add human review queues before adding more autonomous parameter changes.
- Prevent cumulative drift and forbidden parameter combinations.
- Require a measurable evidence window before any strategy adjustment is promoted.
- Treat self-management as another controlled subsystem, not as a hidden optimizer.

### 6.5 Market and Exchange Expansion

The product must be designed to expand beyond NYSE / Nasdaq / S&P 500 without breaking the original system.

Expansion requirements:

- separate market-universe selection from core trading logic;
- separate exchange calendars from agent orchestration;
- allow provider mapping by market pack;
- allow market-specific risk and execution policies by pack;
- require a trust pass on each new market pack before it becomes broadly usable.

The desired sequence is:

1. S&P 500 pack
2. Broader US-equity pack
3. Additional exchange packs outside the initial US scope

---

## 7. Success Measures

| ID | Goal | Success measure |
|---|---|---|
| G1 | Trustworthy autonomy | >=95% of scheduled cycles complete without silent failure over a rolling 30-day window |
| G2 | Explainable silence | 100% of "no trade / no action" outcomes can be answered from controlled surfaces without reading raw logs |
| G3 | Quiet operations | After stabilization, operator intervention is needed on fewer than 20% of healthy trading days |
| G4 | Safe command control | >=95% of accepted phone / Gemma commands execute with correct intent mapping and 0 unsafe bypasses |
| G5 | Controlled execution readiness | All live-adjacent actions are stage-gated, idempotent, reversible, and auditable |
| G6 | Expansion readiness | A new market pack can be added without rewriting the core control plane or agent contracts |

---

## 8. Progress Framework and Indicators

This PRD is intended to be measurable, not merely inspirational.

### 8.1 Maturity Scale

| Level | Meaning |
|---|---|
| 0 | Not started |
| 1 | Foundations exist in code |
| 2 | Observable and testable |
| 3 | Trustworthy under operator scrutiny |
| 4 | Controlled autonomy |
| 5 | Expandable and stable |

### 8.2 Product Progress Snapshot (Evidence-Based, 2026-04-20)

Refreshed from the 2026-04-17 baseline after a code audit against each workstream's move-up criteria. Fuller audit with file references is in `docs/local/temp/prd-v2-progress-audit-2026-04-20.md`.

| Workstream | Current level | Why | What moves it up one level |
|---|---|---|---|
| Core trading runtime | 3 | Scheduler now fails closed on jobstore init; monitor JSON decode emits structured evidence; FinBERT retry trap remains sticky | Close remaining FinBERT retry/recovery trap and finish provider-degradation incident rule |
| Control plane and staged execution | 3 | `ExecutionStageAudit` and stage-transition audit exist; broker idempotency partial via `approval_id` reuse detection | Add CAS-safe `system_state` writes and close remaining broker-submit idempotency gaps |
| Operator evidence and explainability | 4 | Scanner / Analyst / PM / Monitor why-no-action diagnostics shipped with dashboard endpoints; trade narrative stitching available at `/api/trades/narrative` | Extend to Researcher why-no-change and Reporter why-no-alert surfaces; verify narrative-evidence window completeness |
| Self-recovery | 2 | In-process watchdog and control-plane lease renewal exist, but the observer runs in the same process as the scheduler | Add process-external watchdog / health endpoint and fail-loud signaling on recovery-boundary crossings |
| Self-improvement | 2 | Experiment loop, config versioning, and regime overrides exist | Add drift guardrails, parameter-change queue separated from trade approvals, and promotion scorecards |
| Gemma command layer | 0 | No command grammar, typed intent schema, or command audit trail in code | Define command grammar v1 (`status` / `explain`), typed intent schema, and command audit trail |
| Phone-first control surface | 0 | Desktop FastAPI dashboard only; no PWA, responsive workflow, or mobile approval flow | Ship mobile-friendly / PWA control workflow and safe approval flow |
| Multi-exchange readiness | 1 | S&P 500 universe, NYSE calendar, and broker adapter protocol are hardcoded; no market-pack abstraction | Create explicit market-pack boundary with universe / calendar / provider / policy contract |

### 8.3 Operating Progress Indicators

The product should track a small set of top-level indicators continuously:

1. **Trust Index** - composite of silent-failure rate, explainability coverage, approval hygiene, and recovery clarity.
2. **Quiet Operation Rate** - percentage of trading days requiring no user intervention.
3. **Command Safety Rate** - percentage of accepted commands that map correctly and safely to intent schemas.
4. **Shadow Proof Coverage** - percentage of advisory or shadow features with current operator-facing scorecards.
5. **Expansion Readiness Score** - percentage of market-pack contracts and policies that are generalized rather than hardcoded.

These indicators must be visible in the dashboard and later summarized in the phone app.

---

## 9. Worthwhile Pivot Rules

The product should pivot when evidence says the current direction is not earning trust.

| Trigger | Pivot | Stay the course if |
|---|---|---|
| Zero-recommendation days are mostly caused by data-provider degradation | Prioritize market-data reliability over strategy tuning | Diagnostics show the system is intentionally conservative, not broken |
| The dashboard is still required for ordinary daily control | Delay native phone work and refine dashboard workflows first | Daily activity can be safely handled with concise mobile flows |
| Gemma cannot parse commands safely enough | Keep Gemma explanation-only and use deterministic command menus | Safe intent mapping reaches the required confidence and error budget |
| Shadow ML cannot produce repeatable scorecard value | Keep it advisory and pause promotion work | Scorecards show stable value over a meaningful horizon |
| Expansion to non-US markets starts hurting operator trust | Freeze expansion and finish the US control loop first | Market-pack boundaries are stable and trust metrics remain green |

---

## 10. Product Roadmap

### Phase A: Trust Foundation

Objective: make the current system more truthful before making it more autonomous.

Must ship:

- market-data reliability hardening;
- fail-loud scheduler and recovery behavior;
- scanner / PM / monitor why-no-action visibility;
- trade lifecycle narrative;
- shadow-forecast proof loop and scorecard foundations;
- broker idempotency and audited stage transitions.

### Phase B: Quiet Command Layer

Objective: let the user control the system in human words without opening an unsafe free-form channel.

Must ship:

- Gemma command grammar v1;
- typed intent schemas;
- command audit trail;
- command rehearsal mode before execution;
- concise explain commands driven by stored evidence;
- dashboard parity for every command outcome.

### Phase C: Phone-First Operator Control

Objective: make the phone the default daily surface while keeping the dashboard as the deep-trust surface.

Must ship:

- mobile-friendly or PWA workflow for approvals and status;
- concise daily brief and exception digest;
- safe pause / resume / mode change actions;
- one-tap drill into "why" summaries;
- strict notification budget.

Native Android should begin only after the mobile control path proves its value through real use.

### Phase D: Market-Pack Expansion

Objective: grow beyond the initial S&P 500 / US-equity scope without losing control.

Must ship:

- formal market-pack abstraction;
- exchange-calendar abstraction;
- provider configuration by market;
- market-specific policy overlays;
- readiness checklist for every new pack.

---

## 11. Improvements and New Directions That Fit the Spirit of the Project

These improve the product without violating its quiet, controlled nature.

1. **Operator Confidence Ledger** - a single place showing why the operator should trust today's system state: market-data health, last successful run, forced-manual reason, approval backlog, and shadow proof freshness.
2. **Command Rehearsal Mode** - before a high-impact phone or Gemma command executes, show what would happen under current policy and what would be blocked.
3. **Daily Quiet Brief** - one compact summary per day instead of many small interruptions: what ran, what changed, what needs attention, and whether trust increased or decreased.
4. **Trade Narrative Card** - one stitched narrative per trade: why it was selected, why it was sized that way, why it exited, and what the system learned.
5. **Run Capsule Export** - export a single run's evidence, incidents, approvals, and outcomes as a durable bundle for later review.
6. **Market-Pack Readiness Gate** - expansion beyond the initial universe should require a formal checklist, not a code toggle.
7. **Confidence-to-Mobile Gate** - the phone app should not become primary until daily operator tasks can be completed without opening the dashboard in most normal cases.

---

## 12. Non-Goals

The following remain out of scope for this product direction unless explicitly reopened later:

- multi-user accounts;
- social or collaborative trading features;
- a chat-first assistant experience;
- uncontrolled free-form broker actions;
- options, crypto, or broad derivative trading in the first trust-building wave;
- expansion to many exchanges before the original US loop is trustworthy;
- cloud-first operation as a product requirement.

---

## 13. Relationship to Existing Documents

- `docs/PRD.md` remains the preserved original product requirements document.
- This rewrite is the successor PRD for the operator-controlled direction.
- `docs/del/forward-plan-2026-04-17.md` (archived) was the audit-derived roadmap and defect register; superseded by `docs/local/prd-v2-completion-plan-2026-04-20.md`.
- `docs/local/implementation-plan-2026-04-17.md` is the current implementation order and alignment pass for execution.
- `docs/local/prd-v2-completion-plan-2026-04-20.md` is the active Phase A/B completion plan and the primary next-work reference.

This document should be used to keep future planning aligned with the product's spirit: quiet, controlled, explainable, locally governed, and eventually phone-first.
