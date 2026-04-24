# A3 Pipeline Stale Alert Plan

## Context

- Branch: `feat/a3-self-recovery-boundary`
- Anchor commit: `77ed9a7`
- Source residual note:
  `docs/a3-runtime-validation-report-2026-04-23.md`
- Plan artifact:
  `docs/a3-pipeline-stale-alert-remediation-plan-2026-04-24.md`

## Decision

The transient `pipeline_stale` alert noise should be handled as an A3 follow-up
hardening slice, not as a blocker on the lease-reacquire readiness fix.

The first remediation target is alert dispatch truthfulness:

- no configured alert channel should be logged as `alert_delivery_skipped`
- configured channels that fail should still log `alert_delivery_total_failure`
- true stale-pipeline detection and recovery should remain intact

## Next Execution Step

Start at Stage 0 of the remediation plan, then implement Stage 1 if evidence
confirms the validation run had no configured alert channel.

## Execution Update

- Evidence confirmed noisy `alert_delivery_total_failure` was caused by no
  configured local alert route, not by a configured provider failure.
- Implemented alert dispatch truthfulness:
  - no configured channel logs `alert_delivery_skipped`
  - configured webhook / SMTP failure still logs `alert_delivery_total_failure`
- Added regression coverage for:
  - alert skip vs failure semantics
  - fresh active pipeline progress suppressing false `pipeline_stale`
  - stale pipeline recovery remaining intact
- Added tracked report:
  `docs/a3-pipeline-stale-alert-remediation-report-2026-04-24.md`
