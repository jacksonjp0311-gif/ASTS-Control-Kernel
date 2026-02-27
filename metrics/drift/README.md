# Drift Metrics
This directory contains baseline-relative drift computation and multiscale smoothing state.

## What it does
- Computes scalar/per-key drift against a persisted baseline.
- Maintains fast/slow smoothed drift in persisted drift state.

## How it works
- `drift.py` handles baseline load/save and normalized delta math.
- `multiscale.py` performs EWMA-like smoothing over step history.

## Mini directory
- `drift.py`
- `multiscale.py`

## Notes
- Baseline reset behavior directly influences control/recovery sensitivity.
