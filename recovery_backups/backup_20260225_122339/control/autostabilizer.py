import os
from metrics.drift.drift import reset_baseline

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")

def cold_reset():
    # Remove drift accumulators safely
    try:
        os.remove(os.path.join(STATE_DIR, "drift_state.json"))
    except:
        pass

def stabilize_if_needed(drift_slow: float, metrics: dict):
    if float(drift_slow) >= 0.015:
        # Re-anchor baseline
        reset_baseline(metrics)
        return {
            "action": "baseline_reset",
            "reason": "drift_slow_exceeded_0.015"
        }
    return None
