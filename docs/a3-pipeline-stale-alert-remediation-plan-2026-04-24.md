# A3 Pipeline Stale Alert Remediation Plan - 2026-04-24

## Scope

This plan turns the residual A3 runtime-validation note into an executable
follow-up slice. It targets transient `alert_delivery_total_failure` log entries
for `incident_key = pipeline_stale` that appeared during an otherwise healthy
runtime validation run.

The current A3 readiness fix is still valid: `/readyz` returned healthy,
lease-loss/reacquire behavior recovered, and the active pipeline run completed
successfully. This plan is about reducing false or low-value alert noise without
hiding a real stale-pipeline condition.

## Current Evidence

- Reported in `docs/a3-runtime-validation-report-2026-04-23.md`.
- Local note: `docs/local/progress/72198a6-2026-04-23-a3-probe-runtime-validation.md`.
- Runtime symptom:
  - `alert_delivery_total_failure`
  - `incident_key = pipeline_stale`
  - no active incident remained after the run
  - `/readyz` stayed healthy after the A3 probe fix
- Code paths to inspect:
  - stale-pipeline detection: `src/trading/observability/service.py`
    `_latest_expected_pipeline_run_at()`, `_pipeline_progress_is_fresh()`,
    `_evaluate_and_recover()`
  - safe recovery action: `src/trading/observability/service.py`
    `_attempt_pipeline_recovery()`
  - alert delivery: `src/trading/observability/service.py`
    `_dispatch_alerts()`, `_dispatch_webhook()`, `_dispatch_email()`
  - tests: `tests/unit/test_observability.py`

## Working Hypotheses

1. Alert-channel configuration noise:
   `_dispatch_alerts()` logs `alert_delivery_total_failure` whenever both
   webhook and email dispatch return `False`. In local/dev runs this can mean no
   alert channels are configured, not that a configured channel failed.

2. Pipeline-progress freshness gap:
   `pipeline_stale` is suppressed only when `get_pipeline_run_status()` reports
   a running pipeline with fresh `last_progress_at` or `started_at`. If a long
   stage does not update progress often enough, the stale detector can briefly
   open and then resolve a warning during a healthy run.

3. Detection and notification need different thresholds:
   It is useful to record/recover from a stale-pipeline condition quickly, but
   noisy external alert failure logs should require either configured alert
   channels or a condition that survives long enough to matter to an operator.

## Execution Plan

### Stage 0 - Evidence Capture

Goal: identify whether the observed noise was caused by alert channels being
disabled, a true transient `pipeline_stale` open/resolved cycle, or stale
pipeline progress during a long stage.

Actions:

- Query the runtime evidence files listed in the A3 report for
  `pipeline_stale`, `alert_delivery_total_failure`, `alert_dispatch_failed`,
  `pipeline_run_id`, and `correlation_id`.
- Inspect DB-backed evidence for the validation run:
  - `observability.incidents`
  - `observability.recovery_actions`
  - runner `agent_heartbeats`
  - health snapshots around `run_20260423_131247_3c85af1f`
- Confirm whether `alert_webhook_url`, `alert_email_recipients`, and
  `smtp_host` were configured during the run.

Acceptance:

- We can classify the symptom as one of:
  - alert channels disabled but logged as total failure
  - actual configured channel failure
  - true stale-pipeline transient
  - active pipeline progress not being refreshed often enough

### Stage 1 - Alert Dispatch Semantics

Goal: make alert logs truthful without weakening incident detection.

Preferred fix:

- Add an explicit no-channel branch in `_dispatch_alerts()`:
  - if no webhook URL and no complete email route are configured, log a lower
    severity `alert_delivery_skipped` event with
    `reason = no_alert_channels_configured`
  - keep `alert_delivery_total_failure` only when at least one alert route is
    configured and every configured route fails

Tests:

- Add `tests/unit/test_observability.py` coverage proving:
  - unconfigured alert channels do not emit `alert_delivery_total_failure`
  - configured webhook failure still emits the failure path
  - configured email failure still emits the failure path

Acceptance:

- Local/dev runs no longer report "all channels failed" when no channel was
  enabled.
- Real alert delivery failure remains visible and actionable.

### Stage 2 - Pipeline Stale Signal Hardening

Goal: prevent a healthy active run from generating a stale-pipeline notification
unless the run has actually stopped making progress.

Actions:

- Verify whether active pipeline stages call `note_pipeline_progress()` often
  enough for the configured `active_agent_stale_after_seconds` window.
- If progress updates are missing, add progress notes at long-running stage
  boundaries or loops rather than widening the stale threshold globally.
- If the detector still flickers, add a small debounce for notification only:
  require `pipeline_stale` to survive two controller cycles before dispatching
  an external alert, while still recording recovery context immediately.

Tests:

- Extend `tests/unit/test_observability.py` with:
  - active run with fresh progress does not open `pipeline_stale`
  - active run with stale progress still opens `pipeline_stale`
  - transient open/resolved stale condition does not produce an external alert
    before the debounce threshold

Acceptance:

- A genuinely stale pipeline still degrades health and triggers recovery.
- A healthy long-running pipeline does not produce alert noise if progress is
  still fresh.

### Stage 3 - Runtime Proof

Goal: prove the cleanup against the same runtime surface used for A3.

Commands:

```powershell
uv run pytest tests/unit/test_observability.py -k "pipeline_stale or AlertDispatchRetry" --no-cov
uv run pytest tests/unit/test_dashboard_api.py tests/unit/test_observability.py --no-cov
uv run pre-commit run --files src/trading/observability/service.py tests/unit/test_observability.py docs/a3-pipeline-stale-alert-remediation-plan-2026-04-24.md
```

Live drill:

- Start the dashboard on an available local port.
- Confirm `/readyz` is healthy before the run.
- Trigger or observe one scheduler-owned pipeline run.
- Capture:
  - `/readyz`
  - `/api/pipeline/run-status`
  - `/api/observability/incidents`
  - `/api/recovery/actions`
  - dashboard stderr/log events filtered to
    `pipeline_stale`, `alert_delivery_total_failure`, and
    `alert_delivery_skipped`

Acceptance:

- Healthy active run completes without `alert_delivery_total_failure` for
  unconfigured alert channels.
- If no alert channel is configured, logs say alerts were skipped, not failed.
- If a pipeline is deliberately made stale, `pipeline_stale` still opens and
  recovery behavior remains intact.
- `/readyz` remains truthful and does not mask `control_plane_lease` or
  scheduler failures.

## Deliverables

- Code change in `src/trading/observability/service.py`.
- Regression tests in `tests/unit/test_observability.py`.
- Runtime validation update in the A3 report or a new dated follow-up report.
- Hash-prefixed local progress note under `docs/local/progress/`.
- Latest branch CI checked by commit SHA before calling the slice complete.

## Execution Status

- Stage 0 evidence capture: completed.
- Stage 1 alert dispatch semantics: implemented.
- Stage 2 pipeline stale signal hardening: guarded with regression coverage for
  fresh active pipeline progress.
- Stage 3 local verification: completed for the targeted code path.
- Follow-up report:
  `docs/a3-pipeline-stale-alert-remediation-report-2026-04-24.md`
