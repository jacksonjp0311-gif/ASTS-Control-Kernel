# Control

Control-layer policies that shape execution constraints and stabilization actions.

## Files
- `governor_v2.py`: computes execution constraints from drift levels.
- `autostabilizer_v2.py`: cooldown-aware stabilization trigger helper.

## Design
These functions are policy primitives; engine recovery remains the primary decision authority.
