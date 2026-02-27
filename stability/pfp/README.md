# Pulse Feedback Policy (PFP)
This directory contains the PFP overlay used for pulse-based stabilization experiments.

## What it does
- Triggers pulse events from slow-drift and predicted-drift thresholds.
- Persists pulse cooldown state and logs benchmark-relevant pulse telemetry.

## How it works
- `controller.py` computes trigger/contract behavior and writes pulse metadata.
- `prediction.py` estimates one-step drift trend.
- `state_io.py` persists pulse counters and cooldown markers.
- `config.py` resolves PFP thresholds and cooldown settings.

## Mini directory
- `controller.py`
- `prediction.py`
- `state_io.py`
- `config.py`

## Notes
- Keep pulse logic aligned with benchmark analysis fields.
