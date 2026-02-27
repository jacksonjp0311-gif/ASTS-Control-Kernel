# Recovery Backup
This directory contains a legacy recovery snapshot kept for historical reference.

## What it does
- Preserves prior backup copies of runtime-critical modules.

## How it works
- Archive-only. Not a source of truth for active release behavior.

## Mini directory
- `controller.py`
- `runner.py`
- `autostabilizer_v2.py`

## Notes
- Prefer `engine/` and `control/` for current implementation updates.
