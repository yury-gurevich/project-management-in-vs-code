# Shadow Forecast Smoke Runbook

## Goal

Prove one advisory shadow-forecast cycle from model training through matured actualization,
then confirm the same core values appear in CLI output and dashboard surfaces.

## Preconditions

- The local database is reachable.
- `SPY` plus the target candidate symbols already have enough cached daily bars.
- The authenticated dashboard is available locally.
- Azure export is configured if you want to confirm logs-ingestion mirrors the local run.

## Smoke Steps

1. Backfill history only if the status page shows an incomplete shadow-history window.

```powershell
uv run python -m trading.shadow_forecast_cli backfill-history --end-date 2026-04-17
```

2. Train or refresh the current advisory model version.

```powershell
uv run python -m trading.shadow_forecast_cli train-model --as-of-date 2026-04-17
```

3. Run one controlled paper pipeline with shadow forecasting enabled for that process.

Expected proof points:
- one `infer` run is persisted in `shadow_forecast_runs`
- pending rows appear in `shadow_forecast_predictions`
- the latest recommendations carry shadow-forecast rationale fields

4. Confirm the operator surfaces agree before actualization.

```powershell
uv run python -m trading.shadow_forecast_cli report --limit 10
```

Check these values against the authenticated dashboard endpoints:
- `/api/ml/shadow-forecast-status`
- `/api/ml/shadow-forecast-report?limit=10`

Core values that should match:
- `latest_model_version`
- latest `infer` run status
- total / pending prediction counts
- the most recent prediction rows and model version

5. After the configured horizon matures, actualize the pending predictions.

```powershell
uv run python -m trading.shadow_forecast_cli actualize --as-of-date 2026-04-24
```

6. Re-run the report command and confirm matured evidence appears everywhere.

Required proof points:
- CLI report shows non-zero `matured_predictions`
- dashboard report shows the same matured count
- `mae` and `direction_accuracy` are populated
- status shows the latest `actualize` run as `completed`

7. If Azure export is enabled, verify the same cycle reached the external stream.

Required event families:
- `shadow_forecast_run`
- `shadow_forecast_prediction_summary`

## Fail Conditions

- CLI report and dashboard disagree on `latest_model_version`, prediction counts, or matured counts.
- The latest `infer` or `actualize` run is missing from `shadow_forecast_runs`.
- Matured predictions exist in the database but `mae` or `direction_accuracy` remain empty.
- Azure export is enabled but no shadow-forecast run or prediction-summary events arrive.