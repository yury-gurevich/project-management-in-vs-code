# A3 slice: external readiness boundary + recovery action feed

Date: 2026-04-23
Branch: feat/a3-self-recovery-boundary
Base: 5258b3d feat: finish B1 narration scope expansion

## Landed in working tree

- Added unauthenticated `/healthz` and `/readyz` endpoints in `src/trading/dashboard/app.py`.
- `/readyz` now returns `503` when this process is not actually ready to own/run the control plane.
- Readiness payload includes:
  - scheduler state
  - lease ownership / active leader state
  - last successful pipeline run
  - dependency health summary
  - open critical incidents for `scheduler` / `health_controller`
  - explicit readiness blockers
- Added authenticated `/api/recovery/actions` endpoint for a focused recovery feed.
- Recovery action serialization now exposes `requesting_actor`.
- Exported a public `get_control_plane_leader(...)` helper from observability.

## Advantageous pivot taken

Instead of inventing a second readiness subsystem, A3 now rides on the existing health state, control-plane lease store, dependency probes, and recovery-action history. This keeps the boundary truthful while staying small enough to verify cleanly.

## Verification

- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_dashboard_api.py tests/unit/test_observability.py tests/unit/test_gemma_narration.py --no-cov`
  - `132 passed`
- `uv run mypy src/trading --no-incremental`
  - `Success: no issues found in 91 source files`

## Next sensible slice

- Add a small operator runbook doc for probing `/healthz` and `/readyz` from systemd/supervisord/Kubernetes.
- Decide whether the next A3 slice should harden the lease-loss incident trail itself or wire the new readiness endpoints into dashboard help / operator docs first.
