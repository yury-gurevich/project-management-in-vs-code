# Moonshot integration plan — from PRD-v2 to the privacy-first vision

Date: 2026-04-19
Status: working plan, not committed roadmap
Prereqs:
- [docs/PRD-v2.md](../PRD-v2.md) — the product PRD this plan extends
- [docs/moonshots.md](../moonshots.md) — the vision doc
- [docs/future/gemma-capability-evidence.md](gemma-capability-evidence.md) — the capability evidence base

## 1. Reframe — we are not introducing a new vision

The moonshots are **not a parallel direction**. They populate slots PRD-v2
already left open:

| PRD-v2 slot | Moonshot that fills it |
|---|---|
| §5 Local Gemma Control Agent (Level 0 today) | Moonshots #5 (narration), #2 (debate) |
| §6.3 Observability — "Every recommendation must be explainable" | Moonshot #5 narration — already aligned |
| §6.4 Self-management — "human review queues before more autonomy" | Moonshot #3 (self-evolving loop) — but only after review queue exists |
| §11 #1 Operator Confidence Ledger | Moonshot #1 (distribution-based outputs) — natural home for tail-loss / P(profit) |
| §11 #4 Trade Narrative Card | Moonshot #5 narration — direct match |
| §6.4 "deterministic self-improvement first" | Moonshot #4 (causal DAG) — gives self-improvement a *principled* basis |

The work that does **not** fit cleanly into PRD-v2 today and would need an
explicit pivot:
- Moonshot #3 (autonomous PR loop). PRD principle 5 says "evidence before
  automation"; this needs careful framing as a *proposal-only* loop with
  human-gated promotion to fit. Not first wave.

## 2. What PRD-v2 already requires that we now have evidence for

| PRD requirement | What our benchmark proved |
|---|---|
| GEM-01 Local-only command processing | `gemma3:4b` runs locally on consumer-class hardware (16 GB RAM, no GPU) |
| GEM-04 Safe failure on ambiguity | 4B *will* fabricate on open prompts; mitigation = constrain to provided data only. Codifies into prompt design |
| GEM-05 Evidence-grounded explanations | 4B narration cited correct numeric fields and refused to invent. Verified |
| GEM-08 Policy parity | Same broker/control-plane gates apply. Architectural, not model-dependent |
| §11 #4 Trade Narrative Card | 4B narration latency ~34 s/decision is acceptable for this surface |

What our benchmark also proved is *negative* and useful:
- 31B hosted is **not** strictly better — it failed the narration probe
  silently. The "go to cloud for quality" instinct is wrong for this surface.
- 1B is **not** viable. Skip it entirely.
- Open-internet access for sentiment is the wrong design (privacy + source
  quality + tool-call reliability). Use Finnhub feed + RAG over
  `news_embeddings.py` instead.

## 3. Target architecture (from prior session, restated for clarity)

```
Local, no LLM:
  - Moonshot #1: ABIDES distribution outputs       (replaces scalar composite_score)
  - Moonshot #4: causal DAG over signals           (replaces ML-2 weighted sum eventually)
  - FinBERT for article-level polarity             (existing, keep)

Local Gemma 4B (Ollama):
  - Moonshot #5: per-decision narration            (every accept/reject/override)
  - Event/theme extraction over Finnhub articles   (augments FinBERT)
  - GEM-02..08 command parsing + validation        (PRD §5)

Cloud opt-in (Gemma 31B+, behind explicit toggle):
  - Moonshot #2: multi-agent debate                (Pro Mode)

Never:
  - Open-internet web search by Gemma
  - Open-ended "tell me about X" prompts to any local model
```

## 4. Gap analysis — what is already in code, what is missing

### 4.1 What exists today
- Pipeline runner with full agent sequence (`pipeline/runner.py`)
- ObservabilityRuntime with `record_agent_event` and durable event log
- Trade lifecycle events with stitched narrative (`record_trade_lifecycle_event`)
- Control plane state (operating_mode, execution_stage, forced_manual)
- Approval queue and stage transitions (validate_stage_transition)
- Shadow forecasting harness (`ml/shadow_forecast.py`)
- News embeddings infrastructure (`ml/news_embeddings.py`, 386 lines)
- FinBERT pipeline (`services/finbert.py`, 432 lines)
- ABIDES simulation harness (`simulation/abides/`)
- Dashboard with most operator surfaces (3387 lines)

### 4.2 What is missing — the "left to cover our needs" list

#### Group A — Gemma plumbing (PRD §5)
- A1. Local Ollama service wrapper (typed client over the HTTP endpoint)
- A2. Prompt-template registry (versioned, auditable, reusable)
- A3. Structured-output enforcement layer (JSON schema validation, retry on
  malformed, fallback on empty response)
- A4. Hallucination guardrails (input-grounding check: verify every numeric
  claim in output appears in input JSON)
- A5. Audit log row per Gemma call: prompt template id, model, latency,
  retries, output validity, hallucination check result

#### Group B — Distribution-based analyst output (Moonshot #1)
- B1. ABIDES scenario generator (varies order-flow, news timing, queue
  position) — wrapper over existing simulation harness
- B2. New `RecommendationDistribution` schema: `p_profit`, `e_drawdown`,
  `tail_loss_p99`, `time_to_target`, `n_simulations`
- B3. Migration to add JSON column on `Recommendation` (Alembic — fits the
  already-planned migration sprint)
- B4. PM logic update: portfolio construction from distributions instead of
  scalar `composite_score` (Kelly fraction, CVaR budget, optional)
- B5. Backwards-compat shim: keep scalar `composite_score` derived from the
  distribution so existing dashboards / tests still work

#### Group C — Narration layer (Moonshot #5, Trade Narrative Card §11.4)
- C1. Narration trigger points: every accept, reject, override, regime gate,
  promotion, demotion (existing `record_agent_event` is the natural hook)
- C2. Narration prompt templates (per event type) using A2
- C3. Narration storage: extend agent event row OR new `Narration` table
  joined by event id
- C4. Dashboard surface: "Why this happened" panel on every diagnostic /
  recommendation row
- C5. Daily Quiet Brief (PRD §11.3) generator that consumes narrations and
  produces one-page summary

#### Group D — Command layer (Moonshot adjacent, PRD §5.4)
- D1. Command grammar v1 (status, explain, approve, reject, modify, run,
  mode, stage, pause, resume) as Pydantic intent schemas
- D2. Gemma intent-mapping prompt + JSON enforcement (A3)
- D3. Command rehearsal mode (PRD §11.2) — show what would happen before
  executing
- D4. Command audit row (GEM-07) — raw request, parsed intent, validation
  result, actor, outcome
- D5. Dashboard parity check (GEM-08) — every Gemma command produces the
  same control-plane events as the dashboard equivalent

#### Group E — Visibility integration
- E1. New top-level indicators exposed (PRD §8.3):
  - Trust Index now derives from narration coverage % + distribution
    confidence + hallucination guardrail pass rate
  - Quiet Operation Rate stays as defined
  - Command Safety Rate populated by D5 audit data
  - Shadow Proof Coverage extended to cover Gemma outputs (every
    rationale gets a ground-truth flag once outcome is known)
- E2. New incident types: `gemma_unavailable`, `gemma_hallucination_blocked`,
  `gemma_empty_response`, `distribution_simulation_degraded`
- E3. Operator Confidence Ledger view (PRD §11.1) consuming all of the above

#### Group F — Cloud-opt-in mode (Moonshot #2 future)
- F1. Settings flag `pro_mode_enabled` defaulting False
- F2. Provider abstraction so debate can run against Anthropic / Google /
  local 12B+ if user has the hardware
- F3. UX warning before enabling: "this sends ticker, news, and analysis
  data to {provider}. Off by default."
- F4. Runtime guard: refuse pro-mode if `operating_mode = manual` and the
  user has not explicitly re-confirmed in this session

#### Group G — Causal layer (Moonshot #4, future)
- G1. Causal graph schema (nodes = indicators + regime + VIX, edges =
  observed causal direction)
- G2. EconML / DoWhy integration over historical diagnostics
- G3. Counterfactual contribution attribution per recommendation
- G4. Replaces ML-2 weighted-sum once attribution accuracy is validated in
  shadow mode for a meaningful horizon

#### Group H — Self-evolving loop (Moonshot #3, far future)
- H1. Cron-triggered analysis agent over `AnalystDiagnostic` rows
- H2. Indicator-proposal generator (constrained to a small DSL, not arbitrary
  Python)
- H3. Auto-test scaffolder
- H4. Shadow A/B harness for new indicators
- H5. PR-opening agent (proposal-only, never auto-merge)
- H6. Human-gated promotion path that fits PRD §6.4

**Skip H entirely until Group A through E are mature and trusted.** It's the
moonshot that most easily violates "evidence before automation."

## 5. Sequenced phases — how PRD phases extend

PRD-v2 already defines Phase A (Trust Foundation), B (Quiet Command Layer),
C (Phone-First), D (Market-Pack Expansion). The moonshots map as follows:

### Phase A continuation — Trust Foundation (in progress)
*No moonshot work yet.* Finish what PRD-v2 §10 already lists. Trust comes
first.

### Phase B — Quiet Command Layer (extended)
Original PRD-v2 scope:
- Gemma command grammar v1
- typed intent schemas
- command audit trail
- command rehearsal mode
- concise explain commands driven by stored evidence
- dashboard parity for every command outcome

Add:
- **Group A** (Gemma plumbing) — necessary infrastructure for everything else
- **Group C** (Narration) — the "concise explain commands" already in PRD,
  productized as Trade Narrative Card and Daily Quiet Brief
- **Group D** (Command layer) — direct PRD scope, our work just makes it
  buildable
- **Group E1, E2** (Visibility integration of Gemma) — the indicators exist
  in PRD §8.3 already; this populates them

This is where 80% of the moonshot value lands. **Phase B becomes the
moonshot phase**, not a separate effort.

### Phase B+ — Distributions
Insert between PRD-v2's Phase B and Phase C:
- **Group B** (Distribution-based analyst output)
- **Group E3** (Operator Confidence Ledger consuming distributions)

This is the move that *changes the unit of analysis*. Worth a phase of its own
because it touches every downstream component (PM, monitor, reporter,
dashboard, narration prompts).

### Phase C — Phone-First (PRD-v2 unchanged)
Phone-first works because Phase B+ delivered narration and distributions —
the phone surface has something compact and trustworthy to show.

### Phase D — Market-Pack Expansion (PRD-v2 unchanged)
Add only:
- **Group F** (Cloud opt-in) makes sense once expansion brings markets where
  local sentiment data is sparse and cloud assist genuinely adds value. Not
  forced.

### Phase E (new) — Causal layer
- **Group G** — replaces ML-2 weighted sum. Only after distributions ship,
  because the causal graph wants distributional outcomes as the ground truth.

### Phase F (new, possibly never) — Self-evolving loop
- **Group H** — only if and when the entire system has run trustworthily for
  6+ months and the operator wants to delegate the next layer.

## 6. Visibility / management integration

This is the part the user explicitly asked about. Each moonshot needs to be
visible in the dashboard *and* measurable by the PRD §8.3 indicators.

### 6.1 Dashboard panels that need to exist or be extended

| Panel | New / extend | What it shows |
|---|---|---|
| Recommendation evidence | extend | Distribution chart instead of single composite; toggle to see scalar |
| Diagnostic detail | extend | "Why this happened" narration block, with grounding-check status |
| Approval queue | extend | Show distribution + narration on each pending approval |
| Operator Confidence Ledger | new | All E1 indicators in one view; the "trust at a glance" surface |
| Daily Quiet Brief | new | One-page summary surface; consumes narrations |
| Gemma command rehearsal | new | What would happen if this command were executed |
| Gemma audit trail | new | Last N commands, their parsed intent, validation result, outcome |
| Pro Mode toggle | new | Settings panel with explicit warning, off by default |

### 6.2 Observability event types to add

Extend the existing `record_agent_event` taxonomy:

| Event type | When | Data |
|---|---|---|
| `gemma_call_completed` | Every Gemma invocation | template_id, model, latency_ms, retries, output_valid, grounding_passed |
| `gemma_call_failed` | Empty / malformed / timeout | template_id, error_class, attempt_count |
| `narration_generated` | Per narration | event_ref, template_id, narration_id |
| `distribution_computed` | Per candidate | candidate_id, n_simulations, p_profit, e_drawdown, tail_loss_p99 |
| `command_received` | Every Gemma command | raw_request_hash, parsed_intent, validation_result, actor |
| `command_executed` | After validation passes | command_id, control_plane_outcome |
| `pro_mode_toggled` | Explicit user action | enabled, model, confirmed_at |

### 6.3 Indicator wiring (PRD §8.3 made concrete)

| Indicator | Computation |
|---|---|
| Trust Index | weighted: 0.3 × silent_failure_rate + 0.3 × narration_coverage + 0.2 × distribution_confidence_median + 0.2 × grounding_pass_rate |
| Quiet Operation Rate | unchanged: % of trading days with zero operator interventions |
| Command Safety Rate | new: command_executed events with `validation_result = passed` / total commands |
| Shadow Proof Coverage | extend: % of advisory features (shadow ML, narration, distributions) with current operator-facing scorecards |
| Expansion Readiness Score | unchanged |

### 6.4 Control plane states to consider

No new operating modes needed. Existing `paper / broker_shadow / live_manual /
live_autopilot` covers the spectrum.

One new optional setting: `pro_mode_enabled : bool` (Group F1) — orthogonal
to operating_mode. Disable on `forced_manual` until operator re-confirms.

## 7. Risk register

| Risk | Mitigation | Back-out |
|---|---|---|
| 4B narration latency dominates pipeline runtime as candidate count grows | Make narration async — run in background after pipeline, dashboard shows "narration pending" | Disable narration; show structured diagnostic only |
| Gemma fabricates despite grounding check | A4 grounding-check rejects output; operator sees "narration unavailable" instead of garbage | Same as above |
| Distribution computation is too slow on consumer hardware | Adaptive N — start with low N, increase only when latency budget allows | Fall back to scalar `composite_score` for that pipeline run |
| Operator distrusts probabilistic outputs vs scalar score | Backwards-compat shim B5 — keep scalar visible, distribution optional surface | Hide distribution surface until trust earned |
| Pro Mode silently used by accident | F3 + F4 + obvious dashboard banner whenever enabled | Off by default; one-click disable |

## 8. What we explicitly are NOT building (yet)
- Any code in Group H (self-evolving loop)
- Cloud-first anything
- Open-internet sentiment
- Multi-user accounts
- Replacement of FinBERT
- Replacement of existing ML-2 adaptive weights (that's Phase E)

## 9. First sprint candidate (immediately actionable)

The smallest unit of moonshot work that delivers operator-visible value
inside Phase B:

**Sprint goal:** ship Group A (Gemma plumbing) + a *minimum* slice of Group
C (narration on rejection diagnostics only).

Concrete deliverables:
- A1 Ollama service wrapper with retry / timeout / fallback
- A2 Prompt template registry (start with one template: rejection narration)
- A3 JSON schema enforcement (just for narration output: `{narration: str}`)
- A4 Grounding check (verify numeric fields in output appear in input JSON)
- A5 Audit log row per call
- C1 Hook into the rejection path of `analyze_candidate`
- C2 The single rejection narration prompt template
- C3 Add `narration_text` and `narration_status` columns to
  `AnalystDiagnostic`
- C4 Surface "Why rejected" block on the diagnostic detail panel in the
  dashboard
- E2 Two new event types: `gemma_call_completed`, `gemma_call_failed`

This is shippable in one sprint, gives the operator immediate "I can see why
the system said no" value, and establishes every piece of infrastructure
needed for the broader Phase B work.

## 10. Locked-in decisions (2026-04-19)

These are the answers that unblock sprint planning. Reasoning preserved so
they can be revisited with intent, not forgotten.

### D1 — Lazy on-demand narration (not sync, not async)

Pipeline writes the structured diagnostic only. Narration generates **on
first view** in the dashboard ("Why rejected?" click), caches forever.

- No background worker
- No pipeline latency cost
- No wasted compute on diagnostics nobody reads
- Aligns with PRD §3.2 "quiet by default"
- Gemma failure during pipeline becomes a non-event

### D2 — New `Narration` table, polymorphic by event type

Don't extend `AnalystDiagnostic`. Schema:

```python
class Narration:
    id: int
    event_type: str            # 'analyst_diagnostic' | 'approval' | 'exit' | ...
    event_id: int              # FK by convention, polymorphic
    narration_text: str | None # None until first generation
    narration_status: str      # 'pending' | 'generated' | 'unavailable' | 'blocked_by_grounding'
    model_id: str              # 'gemma3:4b@<digest>'
    template_id: str           # 'rejection_v1' etc.
    grounding_passed: bool
    generated_at: datetime | None
    latency_ms: int | None
```

Group C1 lists six narration targets; coupling to one table now means six
migrations later.

### D3 — Pin `gemma3:4b`, capture Ollama digest per call

`gemma_model_id = "gemma3:4b"` in Settings. Audit row records the actual
Ollama digest at call time so tag drift doesn't silently change behaviour.

Tag pinning alone isn't enough for "evidence before automation" — the digest
is what makes a narration reproducible months later.

### D4 — 90 s timeout, 1 retry, then "narration unavailable"

- Per-call timeout: 90 s (generous; benchmark shows 34 s typical)
- On timeout / empty / malformed JSON: 1 retry with same prompt
- On second failure: persist `narration_status = 'unavailable'`, dashboard
  shows "Narration unavailable — retry" button
- On grounding-check failure: persist `narration_status =
  'blocked_by_grounding'`, do **not** show the text, log incident
  (different state — operator should know the system caught a fabrication)

### D5 — Gemma is never load-bearing for trading or control

Universal rule across the whole system:

- Pipeline: Gemma unavailability never blocks
- Approvals: dashboard buttons always work even if Gemma is down
- Commands (future Phase B work): degrade to structured menu equivalents
- Incidents are logged, but no path stops

PRD principle 5 + 6: the dashboard is the reliable substrate; Gemma is one
path among several to operator control, never the only path.

### D6 — Narration is regeneratable

Dashboard "regenerate" button alongside the text. Useful when the model
improves or output is poor. Stores history of regenerations in the audit
log; the `Narration` table keeps only the latest (avoid bloat).

### D7 — Audit log stores prompt + output verbatim

No PII concerns (diagnostic data already in DB). Needed for:
- Debugging hallucinations and grounding failures
- Reproducibility across model digest changes
- Eventually: the corpus that feeds Moonshot #5 phase 2 (fine-tune a local
  model on the system's own reasoning)

Audit row schema:
```python
class GemmaCallAudit:
    id: int
    occurred_at: datetime
    template_id: str
    model_id: str               # tag@digest
    prompt_text: str            # verbatim
    output_text: str | None     # verbatim, None on failure
    output_valid: bool
    grounding_passed: bool | None
    latency_ms: int
    retries: int
    error_class: str | None
    pipeline_run_id: str | None
    narration_id: int | None    # FK if this call produced a narration
```

## 11. First sprint — locked scope

Given D1 through D7, the first sprint shrinks and sharpens:

**Goal:** ship Group A (Gemma plumbing) + minimum slice of Group C
(rejection narration on demand only).

**Must ship:**
- A1 Ollama service wrapper with retry / timeout / fallback per D4
- A2 Prompt template registry — start with one template (`rejection_v1`)
- A3 JSON schema enforcement for narration output: `{narration: str}`
- A4 Grounding check: every numeric value in `narration` must appear in the
  source diagnostic JSON
- A5 `GemmaCallAudit` table per D7
- D2 `Narration` table per D2
- C4 Dashboard "Why rejected" panel on the diagnostic detail view, with:
  - On first open: trigger generation, show spinner
  - On success: display narration + regenerate button (D6)
  - On failure: show "Narration unavailable" + retry button (D4)
  - On grounding-blocked: show "System caught a potential fabrication" + log
    link (no text)
- E2 Two new event types: `gemma_call_completed`, `gemma_call_failed`

**Not in this sprint (deferred to Sprint 2):**
- Narration on accept / approval / exit / override / regime gate
- Daily Quiet Brief
- Operator Confidence Ledger
- Distribution computation
- Command grammar
- Cloud opt-in
