# Operator-Controlled Implementation Plan

**Date:** 2026-04-17  
**Status:** Current after review against `docs/PRD-v2.md`, `docs/del/forward-plan-2026-04-17.md` (archived), and the verified repository state.  
**Purpose:** Turn the rewritten product direction into an execution order that starts with plan errors and misalignments, then sequences new development without losing the current trust-building path.

---

## 1. Currentness verdict

**Yes — the implementation direction is still current, but it needs four explicit corrections before it is used as the main execution plan.**

What remains solid:

- trust, yield, and proof are still the right first priorities;
- market-data reliability is still the main recommendation-yield blocker;
- shadow forecasting still needs proof-loop closure rather than more plumbing;
- control-plane hardening is still required before live-adjacent stages deserve more attention;
- self-improvement should remain deterministic-first.

What changed since the earlier forward plan:

- the product center is now **operator-controlled** rather than implicitly **Master-Agent-centered**;
- the phone path is now a **deferred but real product surface**, not a universal non-goal;
- the next AI-facing work is **local Gemma command and validation**, not a remote Tier 2 proposal loop;
- the implementation plan must now include **command grammar, typed intents, command audit, rehearsal mode, mobile-safe control flow, and market-pack foundations**.

One recent code change does **not** invalidate this plan: `src/trading/ml/news_embeddings.py` now records FinBERT degradation more clearly, but it still keeps the sticky one-process failure mode. The retry / recovery item remains current.

---

## 2. Errors and misalignments to correct first

These are planning errors or wording drifts, not new code defects.

| ID | Misalignment | Why it matters | Correction |
|---|---|---|---|
| P1 | The forward plan still uses **Master Agent** framing in key sections. | PRD v2 centers the operator, dashboard, and local Gemma command layer, not a separate autonomous supervisor as the product face. | Read the observability and self-monitoring work as **operator evidence + control-plane visibility** work. Keep external watchdog work, but do not let naming drag the product toward a chatty supervisor idea. |
| P2 | The forward plan says mobile native is out of scope. | PRD v2 makes the phone path a real late-stage product surface. Rejecting it outright would conflict with the new product direction. | Treat **native Android as deferred**, not rejected. The near-term mobile path is secure mobile-friendly dashboard / PWA, then phone-first control flow, then native Android if earned. |
| P3 | The forward plan's gray AI item is `Anthropic Haiku + queue`. | PRD v2 says the next meaningful AI/control surface is **local Gemma** for command validation and explanation. | De-prioritize remote Tier 2 proposal work below the Gemma local command foundation. Keep remote research suggestions as optional later work, not the next AI milestone. |
| P4 | The forward plan has no implementation stream for command grammar, typed intents, command audit, rehearsal mode, or phone-safe control. | Without these, the product cannot move toward the two-surface model defined in PRD v2. | Add a dedicated **Quiet Command Layer** workstream and a **Phone/PWA control** workstream after the trust-foundation fixes. |
| P5 | The forward plan has no explicit market-pack abstraction work. | PRD v2 requires future expansion beyond the initial US scope without control-plane rewrites. | Add a later-phase **market-pack foundation** stream, but keep it behind trust and command work. |
| P6 | Review-track housekeeping is sitting too close to operational work. | It is low-value compared with reliability, command safety, and control-plane correctness. | Move docs housekeeping to backlog. Do not spend near-term implementation time there. |

---

## 3. Corrected implementation order for the current system

This section is the execution order for work that must happen **before** substantial new product development.

### 3.1 Phase 1: Trust and Truth Fixes

**Goal:** make the existing system more truthful, inspectable, and safe before expanding surfaces.

Priority items:

1. **Fail loud instead of degrading quietly.**
   - Scheduler jobstore failure loudness (`R2`)
   - Monitor JSON decode loss as incident + structured event (`D7`)
   - FinBERT retry / recovery semantics (`R5`, with current observability improvement treated as partial only)
   - Dependency degradation -> incident rule (`M4`)
2. **Stabilize recommendation yield using evidence, not threshold loosening.**
   - Market-data fallback hardening for Massive / Yahoo / Stooq / Wikipedia (`R4`)
   - Distinct degradation reason tags and provenance summaries
   - Scanner / PM / Monitor why-no-action surfaces (`M6`)
3. **Close the shadow proof loop.**
   - Azure ingest validation for a real shadow-forecast run (`M0`)
   - First actualize pass and report parity check
   - Weekly shadow scorecard foundation (`M5` as supporting work, not as a hard-promotion trigger yet)
4. **Expose full trade truth.**
   - Add a stitched trade narrative endpoint and dashboard surface
   - Tie scan -> analyst -> PM -> monitor -> shadow evidence into one readable path

**Exit criteria for Phase 1:**

- zero-recommendation days can be explained without raw logs;
- silent-failure traps are incidents, not hidden warnings;
- shadow forecasting has one complete proof cycle;
- a suspicious operator can reconstruct a trade from controlled surfaces.

### 3.2 Phase 2: Control-Plane Safety

**Goal:** make live-adjacent and control-state behavior deterministic and auditable.

Priority items:

1. Broker submit idempotency (`R3`)
2. CAS-safe `system_state` writes (`R7`)
3. Stage-transition audit trail (`R6`)
4. Correlation across incidents, recovery actions, and master reports (`M2`, `M3`)
5. Cross-portfolio same-stock policy enforcement (`S8`)

**Exit criteria for Phase 2:**

- no last-write-wins control-plane races;
- no duplicate-submit path for broker actions;
- every stage change has actor, reason, and audit evidence;
- dashboard and recovery logic share the same durable state model.

### 3.3 Phase 3: Self-Management Guardrails

**Goal:** finish the deterministic governance layer before adding more autonomy.

Priority items:

1. Cumulative drift guard (`S1`)
2. Forbidden parameter pairs (`S2`)
3. Explicit experiment finalization thresholds (`S3`)
4. Parameter-change queue separated from trade approval queue (`R8`)
5. Shadow-ML scorecard as promotion gate support (`M5`)

**Exit criteria for Phase 3:**

- parameter changes cannot drift silently;
- improvement actions can be reviewed independently of trade approvals;
- advisory ML has a measurable promotion gate.

---

## 4. New development after correction work

Only start these once Phases 1 and 2 are materially complete.

### 4.1 Quiet Command Layer (Gemma local-first)

**Goal:** allow bounded human-language control without opening a free-form unsafe channel.

Implementation slices:

1. **Gemma Slice A - explain-only foundation**
   - command grammar v1 for `status` and `explain`
   - typed intent schemas
   - evidence-grounded response builder
   - audit trail for every parsed request
2. **Gemma Slice B - safe bounded actions**
   - `approve`, `reject`, `modify`, `run`, `mode`, `stage`, `pause`, `resume`
   - rehearsal mode before execution
   - explicit confirmation semantics for risky actions
   - dashboard parity for every command outcome

**Do not start with:** free-form trading chat, autonomous trade invention, or direct broker bypasses.

### 4.2 Phone / PWA Control Surface

**Goal:** make daily control possible from a phone without turning the phone into a full admin console.

Implementation slices:

1. secure mobile-friendly dashboard / PWA shell
2. mobile approval flow and urgent exception flow
3. compact daily status and quiet brief
4. alert transport tuned to bring the user back into the controlled surface

**Native Android** is a later optimization, not the first mobile step.

### 4.3 Market-Pack Foundation

**Goal:** prepare for future market expansion without destabilizing the original US control loop.

Implementation slices:

1. universe-selection abstraction
2. exchange-calendar abstraction
3. provider mapping per market pack
4. market-specific policy overlays
5. readiness checklist for each new pack

This remains later-phase work. Do not start it before the US loop is trustworthy and the command/control model is settled.

---

## 5. Sequencing summary

Use this order unless new evidence disproves it:

1. Trust and truth fixes
2. Control-plane safety
3. Self-management guardrails
4. Gemma quiet command layer
5. Phone / PWA control surface
6. Market-pack foundation
7. Native Android only after mobile control is proven useful

Deferred backlog:

- remote Tier 2 proposal LLM work;
- review-track housekeeping;
- large router/refactor-only work unless it is needed to unblock the phases above.

---

## 6. Confirmation that the plan is still current

**Confirmed current as of 2026-04-17.**

Why this confirmation is defensible:

- the highest-impact defects from the forward audit are still real;
- the newly confirmed analyst and shadow-forecast capabilities are already reflected here as foundations rather than open gaps;
- the repo still has no Gemma command layer, no phone/PWA product flow, no typed command grammar, and no market-pack abstraction;
- the recent FinBERT observability change improves visibility but does not eliminate the retry/recovery work;
- no newer tracked implementation document supersedes this plan.

This plan should be re-checked when any of the following become true:

1. the scheduler and market-data reliability work are complete;
2. the first shadow-forecast actualization scorecard lands;
3. Gemma Slice A is implemented;
4. the first mobile/PWA control workflow ships;
5. market-pack abstractions begin in code.

Until then, this is the current implementation order.

---

## 7. Concrete ticket pack

The concrete Phase 1 engineering ticket pack was archived to `docs/del/phase1-engineering-tickets-2026-04-17.md` once rolled into `docs/local/prd-v2-completion-plan-2026-04-20.md`.