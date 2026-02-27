# Control
This directory contains policy helpers that shape constraints and stabilization behavior.

## What it does
- Computes adaptive execution constraints from drift signals.
- Provides cooldown-aware auto-stabilization hooks.

## How it works
- Functions are consumed by adapters/recovery paths; they do not own orchestration.

## Mini directory
- `governor_v2.py`
- `autostabilizer_v2.py`

## Notes
- Keep deterministic and side-effect-minimal where possible.
