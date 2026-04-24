# Analyst Diagnostics Runbook

## Purpose
Use this after a pipeline run to understand why the analyst produced
recommendations, why it rejected candidates, and whether upstream provider
degradation changed the result.

## Fast Path
1. Run or identify the target `pipeline_run_id`.
2. Open the authenticated dashboard endpoint:
   - `GET /api/analysis/diagnostics`
   - optional params:
     - `pipeline_run_id`
     - `limit`
     - `passed_only`
3. Check the summary first:
   - `candidate_count`
   - `passed_count`
   - `rejected_count`
   - `avg_composite_score`
   - `max_composite_score`
   - `reject_reason_counts`
   - `provider_status_counts`
4. Inspect individual candidate rows for:
   - technical / fundamental / sentiment scores
   - `effective_threshold`
   - `passed`
   - `reject_reason`
   - `top_signals`
   - `provider_status`

## Common Reject Reasons
- `missing_ohlcv`: no cached price history was available for that ticker.
- `regime_blocked`: the market-regime policy blocked new longs.
- `below_threshold`: the candidate scored normally but missed the effective
  threshold.
- `provider_data_unavailable`: Finnhub-dependent slices were unavailable and the
  candidate missed threshold under degraded inputs.
- `price_series_unverified`: the recent technical window was not backed by
  verified adjusted-price rows, so the analyst refused to score it as normal.

## Provider Status Meanings
- `live`: live provider call succeeded during this run.
- `cached_stale`: live provider call failed, but a persisted last-good snapshot
  was reused.
- `unavailable`: neither live data nor a last-good snapshot was available.

## Observability Cross-Check
- Use the observability timeline for the same `pipeline_run_id`.
- Look for:
  - `run_start`
  - `candidate_evaluated`
  - `candidate_rejected`
  - `run_summary`
- Candidate diagnostics and observability details should agree on scores,
  thresholds, reject reasons, incomplete-data flags, and provider status.

## April 15, 2026 Reference Scenario
- Baseline live run:
  - `30` scan candidates
  - `0` analyst recommendations
  - shadow forecasting still produced `30` advisory predictions
- Use this scenario as the reference case when validating that the diagnostics
  surface can explain a zero-yield analyst run without recomputing against live
  APIs.

## What Not To Do Yet
- Do not lower `min_confidence_score` based on a single run.
- Do not treat `provider_data_unavailable` as a signal-tuning problem.
- Do not mix unverified fallback price history into technical scoring.
