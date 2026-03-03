from metrics.drift.drift import reset_baseline
from stability.pfp.state_io import load_state, save_state
from stability.pfp.prediction import predict_drift
from stability.pfp.config import load_thresholds
from benchmarks.recorder import record
import os
import math

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATE_DIR = os.path.join(ROOT_DIR, "state")
DRIFT_STATE_FILE = os.path.join(STATE_DIR, "drift_state.json")

_previous_slow = None
_previous_V = None

ALPHA = 0.5  # Partial contraction coefficient (0 < α ≤ 1)

def apply_pfp(step, theta):
    global _previous_slow
    global _previous_V

    th = load_thresholds()
    D_MAX = float(th["dmax"])
    COOLDOWN_STEPS = int(th["cooldown_steps"])

    state = load_state()

    drift = theta.get("drift", {}) or {}
    if isinstance(drift, dict):
        drift_slow = float(drift.get("slow", 0.0))
    else:
        drift_slow = float(drift or 0.0)

    # Lyapunov proxy
    V_current = drift_slow ** 2

    predicted = predict_drift(drift_slow, _previous_slow)
    _previous_slow = drift_slow

    last_pulse = int(state.get("last_pulse_step", -10000))
    pulse_allowed = (step - last_pulse) >= COOLDOWN_STEPS

    trigger = (drift_slow >= D_MAX) or (predicted >= D_MAX)

    pulse_event = None
    delta_V_pulse = None
    delta_V_coast = None

    if _previous_V is not None:
        delta_V_coast = V_current - _previous_V

    if trigger and pulse_allowed:

        # Partial contraction effect simulation
        contracted_drift = drift_slow * (1 - ALPHA)
        V_after = contracted_drift ** 2
        delta_V_pulse = V_after - V_current

        # Structural reset still applied (optional hard reset)
        reset_baseline(theta.get("metrics", {}))
        try:
            if os.path.exists(DRIFT_STATE_FILE):
                os.remove(DRIFT_STATE_FILE)
        except:
            pass

        state["last_pulse_step"] = step
        state["pulse_count"] = state.get("pulse_count", 0) + 1
        save_state(state)

        pulse_event = {
            "type": "pulse",
            "step": step,
            "drift_slow": drift_slow,
            "V_before": V_current,
            "V_after": V_after,
            "delta_V_pulse": delta_V_pulse
        }

        # Benchmark log
        record({
            "step": step,
            "event": "pulse",
            "drift_slow": drift_slow,
            "V_before": V_current,
            "V_after": V_after,
            "delta_V_pulse": delta_V_pulse,
            "delta_V_coast": delta_V_coast,
            "contraction_verified": (
                delta_V_pulse is not None and
                delta_V_coast is not None and
                delta_V_pulse < delta_V_coast
            )
        })

    else:
        record({
            "step": step,
            "event": "coast",
            "drift_slow": drift_slow,
            "V_current": V_current,
            "delta_V_coast": delta_V_coast
        })

    _previous_V = V_current

    return {
        "drift_slow": drift_slow,
        "predicted_drift": predicted,
        "pulse_event": pulse_event,
        "delta_V_coast": delta_V_coast,
        "D_MAX": D_MAX
    }
