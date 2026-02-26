import json, os
from typing import Dict

STATE = os.path.join(os.path.dirname(__file__), "..", "..", "state", "persist_state.json")

def _load() -> Dict:
    if os.path.exists(STATE):
        try:
            with open(STATE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"count": 0}
    return {"count": 0}

def _save(s: Dict) -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, sort_keys=True)

def persist_over(drift_slow: float, crit: float, steps: int) -> bool:
    s = _load()
    if float(drift_slow) >= float(crit):
        s["count"] = int(s.get("count", 0)) + 1
    else:
        s["count"] = 0
    _save(s)
    return int(s.get("count", 0)) >= int(steps)
