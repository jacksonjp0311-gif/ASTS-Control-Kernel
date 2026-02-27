# State
This directory stores runtime-generated state and diagnostics.

## What it does
- Persists baseline/drift/recovery/PFP state across steps and sessions.
- Holds diagnostic dumps and patch logs for troubleshooting.

## How it works
- Runtime modules read/write JSON state files during execution.
- Diagnostics may accumulate; rotate/archive regularly.

## Mini directory
- `persist_state.json`, `recovery_state.json`, `plateau_state.json`
- `baseline_metrics.json`, `drift_state.json`, `pfp_state.json`
- `core_analysis/`, `core_dumps/`, `patch_logs/`

## Notes
- Operational artifacts only; do not treat as source code.
