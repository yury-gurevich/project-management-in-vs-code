# A3 Pipeline Stale Alert Remediation Report - 2026-04-24

## Scope

Executed the first implementation slice from
`docs/a3-pipeline-stale-alert-remediation-plan-2026-04-24.md`.

The target symptom was noisy `alert_delivery_total_failure` logging during A3
runtime validation when alert channels were not configured. This change does
not weaken `pipeline_stale` detection or automatic recovery.

## Evidence

- `docs/local/temp/a3-active-run-followup.json` contained resolved
  `pipeline_stale` incidents, confirming the stale-pipeline detection/recovery
  path was active.
- `%TEMP%\a3-dashboard-stderr.log` contained `alert_delivery_total_failure`
  entries without paired `alert_dispatch_failed` provider logs, matching the
  no-alert-channel configuration path.
- `.env.example` leaves `ALERT_WEBHOOK_URL`, `ALERT_EMAIL_RECIPIENTS`, and
  `SMTP_HOST` empty by default, which is expected for local validation.

## Fix

- `src/trading/observability/service.py`
  - `_dispatch_alerts()` now checks which alert channels are configured before
    dispatch.
  - if no channel is configured, it logs `alert_delivery_skipped` with
    `reason = no_alert_channels_configured`
  - if one or more channels are configured and all configured routes fail, it
    still logs `alert_delivery_total_failure`

## Regression Coverage

- `tests/unit/test_observability.py`
  - no configured channels skip delivery without calling webhook or email
  - configured webhook failure still reports total alert delivery failure
  - configured SMTP failure still reports total alert delivery failure
  - fresh active pipeline progress suppresses a false `pipeline_stale` incident
  - stale pipeline recovery behavior remains covered by the existing recovery
    test

## Verification

```powershell
uv run pytest tests/unit/test_observability.py::test_health_controller_auto_starts_recovery_for_stale_pipeline tests/unit/test_observability.py::test_fresh_pipeline_progress_suppresses_pipeline_stale_incident tests/unit/test_observability.py::TestAlertDispatchRetry --no-cov -q
uv run pre-commit run --files src/trading/observability/service.py tests/unit/test_observability.py
```

Results:

- targeted pytest: `7 passed`
- changed-file pre-commit: passed

## Remaining Runtime Proof

The next full A3 runtime drill should confirm the same behavior in the running
dashboard logs:

- no `alert_delivery_total_failure` when alert channels are unconfigured
- `alert_delivery_skipped` appears for incidents that would otherwise dispatch
  external alerts
- real stale-pipeline detection and recovery still open recovery actions when a
  pipeline is deliberately stale
