# Engine Recovery

Recovery policy and stateful safety gates.

## Files
- `controller.py`: mode decision ladder (`ok/warn/crit/recover/reset`) with streak/cooldown/rate-limit gates.
- `executor.py`: executes side effects from decisions.
- `persist.py`: persistence detector for repeated threshold breaches.
- `plateau.py`: plateau sensing to detect prolonged boundary behavior.
