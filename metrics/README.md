# Metrics
This directory contains telemetry signal generators used by aggregation and control policies.

## What it does
- Produces drift, divergence, pressure, and horizon-related signals.

## How it works
- Modules are composed by `runtime/telemetry_field/aggregator.py` to produce canonical `theta`.

## Mini directory
- `drift/`
- `divergence/`
- `pressure/`
- `horizon/`

## Notes
- Signal semantics should remain normalized and backward compatible.
