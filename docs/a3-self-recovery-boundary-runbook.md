# A3 Self-Recovery Boundary Runbook

## Goal

Wire the external readiness surface into a real process supervisor so the
dashboard fails loud when the local control plane loses readiness.

The runtime now exposes:

- `/healthz`
  - liveness-style view
  - always returns HTTP `200`
  - includes scheduler state, lease state, dependency summary, active critical
    incidents, and readiness blockers
- `/readyz`
  - readiness view for this local process
  - returns HTTP `200` only when this instance is ready to own and run the
    control plane
  - returns HTTP `503` when the scheduler is stopped, the lease belongs to a
    different instance, or a critical readiness blocker is active

## What To Watch

Treat `/readyz` as the authoritative restart or failover signal.

Expected blocker families:

- `scheduler`
- `database`
- `control_plane_lease`
- `critical_incident:scheduler`
- `critical_incident:health_controller`

Key payload fields:

- `ready`
- `status`
- `scheduler`
- `last_successful_pipeline_run`
- `lease.required`
- `lease.owned`
- `lease.leader`
- `dependency_summary.unhealthy_dependencies`
- `critical_incidents`
- `blockers`

## Local Smoke Check

From the host that runs the dashboard:

```powershell
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
```

Healthy expectation:

- `/healthz` returns `200`
- `/readyz` returns `200`
- `ready` is `true`
- `blockers` is empty

Lease-loss or scheduler-stop expectation:

- `/healthz` still returns `200`
- `/readyz` returns `503`
- `ready` is `false`
- `blockers` includes `control_plane_lease`, `scheduler`, or a critical-incident
  marker

## systemd

Use `/readyz` for the restart decision and `/healthz` for quick diagnostics.

Example unit:

```ini
[Unit]
Description=Trading System Dashboard
After=network.target

[Service]
WorkingDirectory=/opt/traiding-system
ExecStart=/opt/traiding-system/.venv/bin/uv run uvicorn trading.dashboard.app:create_app --factory --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

# Fail loud if the process is up but no longer owns a healthy control plane.
ExecStartPost=/bin/sh -c 'until curl -fsS http://127.0.0.1:8000/readyz >/dev/null; do sleep 2; done'

[Install]
WantedBy=multi-user.target
```

Recommended probe command for external monitoring:

```bash
curl -fsS http://127.0.0.1:8000/readyz
```

If that command exits non-zero, let systemd restart the service or escalate to
the next host-level action.

## supervisord

Example program stanza:

```ini
[program:trading-dashboard]
directory=/opt/traiding-system
command=/opt/traiding-system/.venv/bin/uv run uvicorn trading.dashboard.app:create_app --factory --host 0.0.0.0 --port 8000
autorestart=true
startsecs=5
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/trading-dashboard.out.log
stderr_logfile=/var/log/trading-dashboard.err.log
```

Supervisord itself does not provide native HTTP readiness probes, so pair it
with a small external watcher or cron-style check that restarts the program when
`/readyz` returns `503`.

Example check:

```bash
curl -fsS http://127.0.0.1:8000/readyz || supervisorctl restart trading-dashboard
```

## Kubernetes

Use `/healthz` for liveness and `/readyz` for readiness.

Example container probes:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 15
  timeoutSeconds: 3
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 1
```

Recommended behavior:

- liveness keeps the pod alive while the process is still answering
- readiness removes the pod from service as soon as lease ownership or scheduler
  health is lost
- external orchestration can then replace or reschedule the pod

## Incident Cross-Check

When `/readyz` flips because of lease loss or deliberate scheduler stop, confirm
that the observability surfaces agree:

- `/api/observability/incidents`
- `/api/observability/summary`
- `/api/recovery/actions`

Expected evidence:

- open `scheduler_stopped` incident
- `component` equals `scheduler`
- incident `details.outcome` equals `recovery_stop` for deliberate stop-after-
  lease-loss cases
- recovery actions and readiness blockers tell the same story

## Failure Handling Guidance

Escalate instead of auto-retrying forever when:

- `/readyz` stays `503` after restart
- `database` remains in blockers
- `critical_incident:health_controller` persists
- repeated lease churn causes frequent restarts

In those cases, treat the readiness endpoint as a symptom pointer and inspect
the incident stream plus service logs together.
