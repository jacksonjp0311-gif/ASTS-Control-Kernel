# Runtime
This directory contains observer collection and telemetry field composition.

## What it does
- Collects observer reports and builds canonical runtime telemetry payloads.

## How it works
- `observers/` emits domain metrics.
- `telemetry_field/` normalizes and aggregates those metrics into `theta`.

## Mini directory
- `observers/`
- `telemetry_field/`

## Notes
- Runtime contracts here feed monitoring and recovery directly.
