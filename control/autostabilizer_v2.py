import json
import os
from typing import Optional, Dict, Any
from metrics.drift.drift import reset_baseline

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATE_DIR = os.path.join(ROOT_DIR, "state")

AUTOSTAB_STATE_FILE = os.path.join(STATE_DIR, "autostabilizer_state.json")
DRIFT_STATE_FILE = os.path.join(STATE_DIR, "drift_state.json")

def _load_state() -> Dict[str, Any]:
    if not os.path.exists(AUTOSTAB_STATE_FILE):
        return {"last_reset_step": -10_000}
    try:
        with open(AUTOSTAB_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_reset_step": -10_000}

def _save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(AUTOSTAB_STATE_FILE), exist_ok=True)
    with open(AUTOSTAB_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)

def _cold_reset_multiscale() -> None:
    # Reset multiscale drift accumulator so slow drift can recover after baseline reset.
    try:
        if os.path.exists(DRIFT_STATE_FILE):
            os.remove(DRIFT_STATE_FILE)
    except Exception:
        pass

def stabilize_if_needed_v2(
    step: int,
    drift_slow: float,
    metrics: dict,
    reset_threshold: float = 0.015,
    cooldown_steps: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Returns a dict describing action if stabilization occurs, else None.

    reset_threshold: slow drift level to trigger baseline re-anchor
    cooldown_steps: min steps between resets
    """
    drift_slow = float(drift_slow or 0.0)
    step = int(step if step is not None else 0)

    s = _load_state()
    last = int(s.get("last_reset_step", -10_000))

    # Cooldown prevents repeated resets
    if (step - last) < int(cooldown_steps):
        return None

    if drift_slow >= float(reset_threshold):
        # advisory only
        _cold_reset_multiscale()
        s["last_reset_step"] = step
        _save_state(s)
        return {
            "action": "baseline_reset_and_driftstate_cold_reset",
            "reason": f"drift_slow_exceeded_{reset_threshold}",
            "step": step,
            "cooldown_steps": int(cooldown_steps)
        }

    return None

