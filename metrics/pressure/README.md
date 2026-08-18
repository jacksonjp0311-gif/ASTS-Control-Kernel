# Pressure Metrics

How close the loop is to its load budget.

## What it does
- Reads load keys: `usage`, `latency`, `load`, `cpu`, `memory`
- Values in [0, 1] are fractions of capacity; values above 1 are divided by `MAX_BUDGET`
- Returns the hottest load key, or `None` (UNKNOWN) when none are present

## Mini directory
- `pressure.py`
- `budgets.py`

## Notes
- Witness only. Can raise `warn`. Cannot promote `reset`.
- Calibrate `MAX_BUDGET` against real traces when adapters stop being synthetic.
