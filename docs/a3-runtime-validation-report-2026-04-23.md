# A3 Runtime Validation Report - 2026-04-23

## Scope

Validated the A3 self-recovery boundary on `feat/a3-self-recovery-boundary` after
fixing a false-negative readiness bug in the external probe path.

## What Was Fixed

- Root cause: `/healthz` and `/readyz` were consuming the annotated dependency
  summary as if every top-level value were a dependency row. Operator-timezone
  metadata (`display_timezone`) triggered an internal `AttributeError`, which
  left `lease.leader = null` and incorrectly surfaced `control_plane_lease` as a
  blocker.
- Fix:
  - `build_dependency_status_summary()` now returns only named dependency rows.
  - `_build_external_probe_payload()` now filters dependency items defensively
    before computing blockers.

## Quality Gate

- `uv run pre-commit run --files src/trading/dashboard/app.py src/trading/observability/service.py tests/unit/test_dashboard_api.py tests/unit/test_observability.py`
- `uv run mypy src/trading --no-incremental`
- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_dashboard_api.py tests/unit/test_observability.py --no-cov`

Result:

- `pre-commit`: passed
- `mypy`: passed
- `pytest`: `106 passed`

## Live Runtime Trace

Evidence files used during validation:

- `docs/local/temp/a3-runtime-validation-fixed.json`
- `docs/local/temp/a3-manual-run-validation.json`
- `docs/local/temp/a3-active-run-followup.json`
- `docs/local/temp/a3-lease-drill.json`
- `%TEMP%\\a3-dashboard-stderr.log`

Observed behavior:

1. Dashboard started successfully on `http://127.0.0.1:8001`.
2. Observability runtime started and then acquired control-plane leadership:
   - `observability_started`
   - `control_plane_leadership_acquired`
3. External probes turned green on the patched code:
   - `/healthz` -> `200`
   - `/readyz` -> `200`
   - `ready = true`
   - `blockers = []`
   - `lease.owned = true`
4. A dashboard-triggered manual run attempt returned `409` because a scheduler /
   observability-owned run was already active. This is correct single-flight
   behavior for A3.
5. The active pipeline run completed successfully:
   - run id: `run_20260423_131247_3c85af1f`
   - final state: `succeeded`
   - final stage: `completed`

## Lease-Loss Drill

Acceptance criterion validated live against the running app:

- Before drill: `/readyz` returned `200` with `ready=true`.
- External lease override: writing a different active leader into
  `observability.control_plane_leader` caused `/readyz` to flip to `503` with
  `blockers=["control_plane_lease"]`.
- Recovery: expiring that external leader let the app reclaim leadership and
  return `/readyz` to `200` with `blockers=[]` and the local dashboard instance
  visible again as the leader.

While validating this path I found and fixed one more A3 defect:

- After lease reacquire, the dashboard could reclaim leadership without
  restarting the already-stopped local control plane because
  `local_control_plane_started` was sticky.
- The fix now restarts the scheduler / observability lane when leadership is
  reacquired and the local control plane is no longer active.

## Data Ingestion And Dashboard Visibility

The live run produced matching backend and dashboard evidence:

- Regime and macro context were recorded:
  - `VIX: 19.50`
  - `Regime context: bull_low_vol`
- Scanner pipeline moved end-to-end:
  - `Fetched 503 S&P 500 tickers from Wikipedia`
  - `Universe: 503 tickers`
  - `Filters passed: 226 candidates`
  - `Scanner complete: 30 candidates written to scan_results`
- Analyst stage executed on those candidates and produced `0` recommendations for
  this run because everything remained below threshold.
- Monitor and reporter stages completed, and the runner logged
  `Pipeline completed successfully`.
- Dashboard / observability state after completion:
  - `/readyz`: healthy (`200`, `ready=true`)
  - `/api/pipeline/run-status`: `succeeded`
  - `/api/observability/incidents`: `0` active incidents
  - `/api/recovery/actions`: historical actions present, but no new recovery was
    required for this run

## Residual Notes

- During the active run, logs still showed transient `alert_delivery_total_failure`
  entries for `incident_key = pipeline_stale`. These did not leave an active
  incident and did not block readiness after the probe fix, but they are worth
  treating as the next cleanup slice because they add alert noise during an
  otherwise healthy run.

## Follow-Up Remediation Plan

The actionable follow-up for the `pipeline_stale` alert noise is now tracked in
`docs/a3-pipeline-stale-alert-remediation-plan-2026-04-24.md`.

The plan separates two concerns that should not be collapsed:

- keep `pipeline_stale` detection and recovery intact for truly stale runs
- stop local/dev alert-channel gaps from being logged as
  `alert_delivery_total_failure` when no alert channel was configured
