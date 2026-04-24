# Cloud Gemma Dev Mode

**Status:** Active in checked-in runtime — dev-only resource-constraint deviation
**Decided:** 2026-04-20
**Owner:** Yury Gurevich
**Scope:** Development and early-stage operator trials. Not a product decision.

---

## 1. What this is

For the foreseeable dev period, the trading system's Gemma integration calls the **hosted Google Gemma API (`google.genai`) with `gemma-4-31b-it`** instead of running Gemma locally via Ollama. This is a temporary operational deviation from PRD-v2 principles, driven by hardware limits — not a change in product direction.

## 2. Why

- The target workstation (16 GB RAM, Intel Iris Plus 640, CPU-only) cannot host Ollama + `gemma3:4b` + the rest of the trading stack concurrently. Benchmarks in [gemma-capability-evidence.md](../future/gemma-capability-evidence.md) confirm 60–89 s per call under constrained memory, and the app itself competes for the same RAM.
- Ollama's hosted/cloud inference pricing makes it an expensive substitute for development volume.
- Google AI Studio provides a free-tier API key for `gemma-4-31b-it`, and [test.py](../../test.py) has already proven end-to-end connectivity from this project.
- The hosted 31B model, per the project's own benchmarks, produces **higher-quality grounded output** than the local 4B target on the narration task. Quality is not the reason we're going local later — privacy is.

## 3. PRD deviation and what remains intact

**Deviated:**
- PRD-v2 §3 Principle 4 — *"Local control of meaning."* Command interpretation and explanation prompts now leave the operator's machine during dev mode.
- PRD-v2 §3 Principle 9 — *"Cloud is later, not first."* Cloud is first during dev mode. (Note: the PRD says "later, not first," it does **not** say "never.")
- PRD-v2 §5 Gemma scope — *"primary command and explanation path must run locally"* (GEM-01). GEM-01 is on hold until Phase 1 of the exit plan below.

**Still intact and unchanged:**
- GEM-02 through GEM-08 — allowed intent grammar, typed command schemas, safe failure on ambiguity, evidence-grounded explanations, high-risk confirmation, durable audit, policy parity. All of these are backend / policy requirements and are unaffected by where the model runs.
- Every other PRD-v2 principle: quiet by default, controlled channels only, evidence before automation, dashboard-for-trust, expansion-must-be-architectural.
- The product direction and PRD-v2 text itself. **This runbook is the only document marking the deviation;** PRD-v2.md is not edited.

## 4. Privacy cost (explicit)

In dev mode, every Gemma call sends structured diagnostic data (ticker, scores, thresholds, reject reasons, signal names) to Google's Gemma API endpoint. Assume standard Google AI Studio data handling applies. Specifically:

- **What leaves the machine:** the prompt body, which includes diagnostic payloads (no broker credentials, no account balances, no order quantities).
- **What does not leave:** broker API keys, positions, P&L, portfolio sizing, or any mutation path. Gemma in dev mode is explanation-only plus eventually typed commands that are validated locally before any state change.
- **Who approved:** the operator (single-user product). No third-party data is in scope because there is no third-party data in the system.

The operator accepts this cost as a dev-mode trade against blocked progress.

## 5. Scope of the deviation

Applies to:
- Narration MVP (Phase B Stage B0) and all narration scope expansion (B1).
- Gemma explain-only command layer (B2) and bounded action command layer (B3).
- Command rehearsal mode (B4) and Daily Quiet Brief (B5).

Does not apply to:
- Any non-Gemma component. The rest of the pipeline remains entirely local.
- Any production / live-trading deployment. Live-adjacent stages (`broker_shadow`, `live_manual`, `live_autopilot`) are not approved to call cloud Gemma without a fresh decision.

## 6. Exit plan — when this runbook is retired

This deviation is retired when **all** of the following are true:

1. The operator's workstation is upgraded with enough headroom to run Ollama + `gemma3:4b` Q4 + the trading stack concurrently without memory pressure (rough target: 32 GB RAM, dedicated GPU or faster CPU).
2. A fresh local benchmark reproduces the findings in [gemma-capability-evidence.md](../future/gemma-capability-evidence.md) §"Verdict by moonshot" under the upgraded hardware (≤ 45 s narration latency at 4B Q4).
3. The Gemma client module is rewritten to target the local Ollama HTTP endpoint. At that point the cloud client stays as dead code if and only if there's a justified dual-mode use case; otherwise it is deleted.
4. GEM-01 is re-enabled in the PRD checklist and this runbook is moved to `docs/local/progress/` as a closed record.

No intermediate steps. The deviation ends when the workstation allows it.

## 7. Implementation expectations

For engineers picking up Gemma-related sprints during dev mode:

- **Model:** `gemma-4-31b-it` via `google.genai`. Do not silently switch models; model choice is audited.
- **SDK:** `google-genai` Python package. Add to `pyproject.toml` if not present; do not bring in alternate wrappers.
- **Auth:** `GEMMA_API_KEY` environment variable. Already present as `Settings.gemma_api_key` in [src/trading/core/config.py](../../src/trading/core/config.py). Never hardcode.
- **Endpoint routing:** `GEMMA_ENDPOINT` is retired in cloud dev mode. The `google.genai` SDK owns endpoint selection and timeout wiring.
- **Network boundary:** the only external endpoint the Gemma module may contact is Google's AI Studio Gemma API. Any other outbound URL from `src/trading/gemma/` is a security bug.
- **Grounding and refusal rules** from PRD §5.3 remain unchanged and enforced locally in the Python code, not trusted to the model.
- **Rate limiting:** design for Google AI Studio free-tier quotas. On quota exhaustion, narration / command endpoints must return a structured "unavailable" state, not 500.
- **Audit:** every call records `model_id="gemma-4-31b-it"` and the API response's model version string (when provided). In persisted rows the dashboard may surface this as `gemma-4-31b-it@<model_version>`. There is no local Ollama digest concept to capture.
- **Dev-mode banner:** any dashboard surface that displays Gemma output must show a small, unobtrusive "cloud dev mode" indicator so the operator never forgets the privacy context.

## 8. References

- [docs/PRD-v2.md §3, §5](../PRD-v2.md) — principles and Gemma scope (untouched).
- [docs/local/prd-v2-completion-plan-2026-04-20.md](prd-v2-completion-plan-2026-04-20.md) — Phase A + B completion plan; B0 is marked cloud-for-now.
- [docs/del/sprint-gemma-narration.md](../del/sprint-gemma-narration.md) — archive pointer for the shipped narration MVP sprint, with recovery instructions for the original full spec.
- [docs/future/gemma-capability-evidence.md](../future/gemma-capability-evidence.md) — capability benchmarks; recommended-architecture section notes this dev-mode pivot.
- [test.py](../../test.py) — working proof-of-life call against `gemma-4-31b-it` via `google.genai`.
