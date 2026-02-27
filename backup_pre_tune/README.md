# Backup: pre-tune
This directory is a historical snapshot from before tuning changes.

## What it does
- Preserves old controller/persistence files for forensic comparison.

## How it works
- Not part of active runtime import paths; should remain read-only.

## Mini directory
- `controller.py`
- `persist.py`

## Notes
- Treat as archive material. Do not evolve active release behavior here.
