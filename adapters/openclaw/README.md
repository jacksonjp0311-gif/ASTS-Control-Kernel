# OpenClaw Adapter

Bridges OpenClaw skill calls into ASTS kernel execution.

## Files
- `skill_entry.py`: base skill entry using `engine.execution.runner.run_step`.
- `adaptive_skill_pfp.py`: base skill + pulse feedback control.
- `adaptive_skill_v2.py`: base skill + governor/autostabilizer v2 hooks.
- `adapter.py`: simple adapter shim.

## Contract
All skill functions accept `env: dict` and return a dict containing `theta` telemetry payload.
