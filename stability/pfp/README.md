# Pulse Feedback Policy (PFP)

Optional pulse controller layered above base ASTS step execution.

## Files
- `controller.py`: pulse trigger, contraction estimate, state updates.
- `prediction.py`: one-step drift extrapolation.
- `state_io.py`: persistent pulse state I/O.
- `config.py`: threshold loading with sensible defaults.
