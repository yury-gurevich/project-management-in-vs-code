# B1 Finish Audit

- Date: 2026-04-23
- Branch: `feat/b1-narration-scope-expansion`
- Branch tip at audit start: `a3eed0a`

## What is already in the working tree

- B1 narration slices already coded and covered in tests:
  - dependency incidents
  - monitor no-exit diagnostics
  - exit decisions
  - stage transitions
  - approval outcomes
- Targeted verification on 2026-04-23 passed:
  - `.venv\Scripts\python.exe -m pytest tests/unit/test_dashboard_api.py tests/unit/test_gemma_narration.py tests/unit/test_gemma_templates.py --no-cov`
  - result: `101 passed`

## What still needs to be finished for B1

- `regime-gate transitions`
  - no dedicated B1 template or specialized narration flow exists yet
  - best-fit durable source is existing `AnalystDiagnostic` rows with `reject_reason="regime_blocked"`
- `shadow-forecast scorecard summaries`
  - scorecard data source exists already via `build_shadow_scorecard()` and `/api/ml/shadow-scorecard`
  - no Gemma template, narration event type, or explain wiring exists yet
  - narration cache needs refresh behavior because this is a computed summary, not a single persisted row

## Chosen completion path

- Finish `regime-gate transitions` first by specializing the existing analyst-diagnostic narration path for `regime_blocked` diagnostics instead of inventing a new durable table.
- Finish `shadow-scorecard summaries` second by keying narration on `window_days` and refreshing cached narration when newer shadow rows exist than the stored narration timestamp.

## Risks to watch

- Do not fork the B0/B1 narration framework just for summary-style scorecards.
- Keep the branch narrow; avoid adding unrelated narration surfaces while closing B1.
