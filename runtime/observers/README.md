# Runtime Observers
This directory contains domain observer implementations.

## What it does
- LIVE: `resources` and `runtime` come from `host_process`. `--simulate`: those two slices switch to `runtime/observers/plant.py` and are labeled `source: simulation`.
- `code`, `reasoning`, and `integration` stay synthetic in both modes.

## Mini directory
- `code_structure.py`
- `runtime_exec.py`
- `reasoning_quality.py`
- `resources.py`
- `integration.py`
- `base.py`

## Notes
- Observer keys and scales affect drift computation and alert behavior.
