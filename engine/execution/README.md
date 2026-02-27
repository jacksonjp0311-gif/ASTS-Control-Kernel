# Engine Execution
This directory contains session and step orchestration utilities.

## What it does
- Drives each ASTS loop iteration and session lifecycle.

## How it works
- `runner.py` executes full step flow and writes ledger events.
- `scheduler.py` provides deterministic ordering helpers.
- `environment.py` prepares execution environment payloads.

## Mini directory
- `runner.py`
- `scheduler.py`
- `environment.py`

## Notes
- Keep execution ordering deterministic and side-effects explicit.
