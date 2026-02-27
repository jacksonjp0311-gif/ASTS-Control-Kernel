# Engine Recovery
This directory defines ASTS recovery policies, gates, and recovery-related state helpers.

## What it does
- Decides recovery modes (`ok/warn/crit/recover/reset`).
- Enforces cooldown/rate-limit/streak logic and plateau/persistence sensing.
- Executes approved recovery actions in one side-effect boundary.

## How it works
- `controller.py` computes decisions.
- `executor.py` applies side effects.
- `persist.py` and `plateau.py` track bounded historical conditions.

## Mini directory
- `controller.py`
- `executor.py`
- `persist.py`
- `plateau.py`

## Notes
- New recovery actions should be wired through `executor.py`.
