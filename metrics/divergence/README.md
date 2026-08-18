# Divergence Metrics

Inter-report disagreement on a shared [0, 1] field.

## What it does
- Confidence-weighted mean absolute deviation across observer slices
- Returns `None` (UNKNOWN) when fewer than two usable reports exist

## Mini directory
- `divergence.py`

## Notes
- Witness only. Can raise `warn`. Cannot promote `reset`.
- 0 = observers agree. 1 = two reports at opposite ends of the unit interval.
