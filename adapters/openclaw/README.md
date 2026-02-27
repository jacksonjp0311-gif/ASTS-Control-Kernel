# OpenClaw Adapter
This directory provides OpenClaw-facing skill wrappers for ASTS.

## What it does
- Bridges OpenClaw skill calls to ASTS step execution.
- Adds optional policy overlays (PFP and v2 adaptive constraints).

## How it works
- `skill_entry.py` calls the base engine step function and normalizes return shape.
- Optional wrappers enrich output with pulse-control or constraint/stabilization annotations.

## Mini directory
- `skill_entry.py`
- `adaptive_skill_pfp.py`
- `adaptive_skill_v2.py`
- `adapter.py`

## Notes
- Expected interface: input `env: dict` -> output dict including `theta`.
