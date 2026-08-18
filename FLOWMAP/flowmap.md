# ASTS Runtime Flow Map

## Entry Point
main.py

main.py
  ↓
runtime/session start
  ↓
engine.execution.runner
  ↓
adapters.host_process (RSS + previous-step wall)
  ↓
Telemetry Capture (live usage/latency + synthetic plant)
  ↓
metrics.drift + metrics.divergence + metrics.pressure
  ↓
Threshold Evaluation
  ↓
stability.pfp.controller
  ↓ (delegates)
engine.recovery.controller.decide()
  ↓
Recovery Decision Object
  ↓
engine.recovery.controller.apply()
  ↓
Optional reset_baseline()
  ↓
Backoff Adjustment
  ↓
Ledger append (ledger.jsonl hash chain)
  ↓
Next Step Loop
  ↓
Session Complete

---

## Control Escalation Ladder

drift_slow >= warn      → warn
drift_slow >= crit      → crit
drift_slow >= recover   → recover
drift_slow >= reset     → reset (gated)

Autonomous escalation:
warn streak → recover
crit streak → reset (if gate open)
plateau detected → recover

Cooldown + rate limit enforce reset gating.
