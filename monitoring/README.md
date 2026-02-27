# Monitoring
This directory provides operator-facing assessment and telemetry output helpers.

## What it does
- Evaluates warning/critical thresholds and recommended actions.
- Prints telemetry snapshots for each runtime step.

## How it works
- `alerts.py` evaluates conditions.
- `monitor.py` renders operator output and status bundles.

## Mini directory
- `monitor.py`
- `alerts.py`
- `dashboards/`

## Notes
- Keep alert semantics synchronized with recovery thresholds where intended.
