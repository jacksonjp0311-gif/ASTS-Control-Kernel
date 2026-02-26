import json
import os
from typing import Dict

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "state")
DRIFT_STATE_FILE = os.path.join(STATE_DIR, "drift_state.json")

def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))

def _load_state() -> Dict:
    if not os.path.exists(DRIFT_STATE_FILE):
        return {"fast": 0.0, "slow": 0.0, "k": 0}
    with open(DRIFT_STATE_FILE, "r", encoding="utf-8") as f:
        s = json.load(f)
    return {
        "fast": _clamp01(s.get("fast", 0.0)),
        "slow": _clamp01(s.get("slow", 0.0)),
        "k": int(s.get("k", 0))
    }

def _save_state(state: Dict) -> None:
    os.makedirs(os.path.dirname(DRIFT_STATE_FILE), exist_ok=True)
    with open(DRIFT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)

def multi_scale(D_k: float, a_fast: float = 0.65, a_slow: float = 0.93) -> Dict[str, float]:
    """"Update and return multiscale drift components (persisted)."""""
    D_k = _clamp01(D_k)
    a_fast = max(0.0, min(0.999, float(a_fast)))
    a_slow = max(0.0, min(0.9999, float(a_slow)))

    s = _load_state()
    fast_prev = _clamp01(s["fast"])
    slow_prev = _clamp01(s["slow"])

    fast = _clamp01(a_fast * fast_prev + (1.0 - a_fast) * D_k)
    slow = _clamp01(a_slow * slow_prev + (1.0 - a_slow) * D_k)

    out = {"fast": fast, "slow": slow, "k": int(s["k"]) + 1}
    _save_state(out)
    return out
