# A3 slice: lease-loss fail-loud scheduler stop

Date: 2026-04-23
Branch: feat/a3-self-recovery-boundary
Base: 9ebdb88 feat: add A3 readiness boundary endpoints

## Landed in working tree

- Hardened the observability lease-loss path so losing the control-plane lease now persists a visible `scheduler_stopped` incident before the local scheduler is stopped.
- The incident details now carry:
  - `outcome: recovery_stop`
  - `stop_reason: control_plane_leadership_lost`
  - the winning/active `leader` payload when available
  - an operator-facing explanation for why the scheduler was deliberately stopped
- Added an observability regression test proving the incident becomes visible through the summary feed after lease loss.

## Why this slice was next

The advantageous pivot was to finish the fail-loud behavioral contract before writing the operator runbook. `/readyz` was already truthful for readiness, but the PRD also asked that scheduler stop events be externally visible with recovery-stop semantics. This slice closes that behavioral gap first.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_observability.py tests/unit/test_dashboard_api.py -k "lease_loss_records_visible_scheduler_recovery_stop_incident or control_plane_leader or readyz or healthz or recovery_actions_endpoint" --no-cov`
  - `6 passed`
- `uv run pre-commit run --all-files`
  - passed
- `uv run mypy src/trading --no-incremental`
  - passed
- `uv run pytest`
  - `1231 passed`
  - coverage `80.17%`

## Remaining A3 follow-on

- Add the operator runbook for wiring `/healthz` and `/readyz` into systemd / supervisord / Kubernetes probes.
