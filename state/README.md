# State

Runtime-persisted kernel state and diagnostics.

## Typical files
- `baseline_metrics.json`, `drift_state.json`, `pfp_state.json`
- `persist_state.json`, `recovery_state.json`, `plateau_state.json`
- `core_analysis/`, `core_dumps/`, `patch_logs/`

## Guidance
State files are operational artifacts, not source code. Keep this directory bounded and rotate large diagnostics.
