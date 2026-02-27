# Engine
This directory is the ASTS runtime core for execution and recovery decisions.

## What it does
- Orchestrates per-step observer->telemetry->assessment->recovery flow.
- Applies deterministic recovery policy with persisted safety gates.

## How it works
- `execution/` runs sessions and step pipelines.
- `recovery/` decides modes and executes approved side effects.

## Mini directory
- `execution/`
- `recovery/`

## Notes
- This is the primary truth surface for runtime behavior.
