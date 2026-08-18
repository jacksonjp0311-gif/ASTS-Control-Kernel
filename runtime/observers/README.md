# Runtime Observers
This directory contains domain observer implementations.

## What it does
- Produces observer reports. `resources` and `runtime` are live (`host_process`). `code`, `reasoning`, and `integration` remain synthetic plant slices.

## Mini directory
- `code_structure.py`
- `runtime_exec.py`
- `reasoning_quality.py`
- `resources.py`
- `integration.py`
- `base.py`

## Notes
- Observer keys and scales affect drift computation and alert behavior.
