import json, os
from typing import Dict, Any, List

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "state")
PLATEAU_FILE = os.path.join(STATE_DIR, "plateau_state.json")

def _load():
    if os.path.exists(PLATEAU_FILE):
        try:
            return json.load(open(PLATEAU_FILE, "r", encoding="utf-8"))
        except Exception:
            return {"slow": []}
    return {"slow": []}

def _save(s):
    os.makedirs(os.path.dirname(PLATEAU_FILE), exist_ok=True)
    json.dump(s, open(PLATEAU_FILE, "w", encoding="utf-8"), indent=2, sort_keys=True)

def push_and_check(drift_slow: float, window: int = 6, eps: float = 1.5e-4) -> Dict[str, Any]:
    """
    Plateau detector: if drift_slow stays in a tight band for `window` steps,
    we consider the system 'stuck' and eligible for escalation.
    """
    s = _load()
    arr: List[float] = s.get("slow", [])
    try:
        x = float(drift_slow)
    except Exception:
        x = 0.0
    arr.append(x)
    if len(arr) > int(window):
        arr = arr[-int(window):]
    s["slow"] = arr
    _save(s)

    if len(arr) < int(window):
        return {"plateau": False, "span": None, "mean": sum(arr)/max(1,len(arr))}

    mn = min(arr); mx = max(arr)
    span = mx - mn
    mean = sum(arr)/len(arr)
    return {"plateau": (span <= float(eps)), "span": span, "mean": mean}

# ------------------------------------------------------------
# Plateau sensing — lightweight, deterministic, safe
# Adds: check(theta, root_dir) -> dict
# ------------------------------------------------------------
import os
import json
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "state", "plateau_state.json")

def _load():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8-sig") as f:
                x = json.load(f)
                return x if isinstance(x, dict) else {}
    except Exception:
        pass
    return {}

def _save(obj: dict):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
    except Exception:
        pass

def check(theta: dict, root_dir: str) -> dict:
    """
    Plateau = "system is stuck near a boundary for too long".
    This is not a solver; it's a sensor:
      - tracks streaks of elevated slow drift
      - tracks repeated warn/crit-like signals
    Returns a dict suitable for ledger attachment.
    """
    th_path = os.path.join(root_dir, "state", "thresholds.json")
    th = {}
    try:
        if os.path.exists(th_path):
            with open(th_path, "r", encoding="utf-8-sig") as f:
                x = json.load(f)
                if isinstance(x, dict):
                    th = x
    except Exception:
        th = {}

    warn = float(th.get("slow_drift_warn", th.get("warn", 0.006)))
    # plateau window + threshold can be tuned; defaults are conservative
    window = int(th.get("plateau_window", 5))
    min_hits = int(th.get("plateau_min_hits", 4))

    d = theta.get("drift", {})
    drift_slow = 0.0
    try:
        if isinstance(d, dict):
            drift_slow = float(d.get("slow", 0.0))
        else:
            drift_slow = float(d)
    except Exception:
        drift_slow = 0.0

    s = _load()
    hits = int(s.get("hits", 0))
    steps = int(s.get("steps", 0))

    steps += 1
    # hit if we are above warn (plateau boundary behavior)
    if drift_slow >= warn:
        hits += 1
    else:
        # decay slowly rather than reset hard
        hits = max(0, hits - 1)

    # maintain bounded window
    if steps > window:
        steps = window
        # keep hits bounded too
        hits = min(hits, window)

    plateau = bool(hits >= min_hits and steps >= window)

    out = {
        "plateau": plateau,
        "hits": hits,
        "window": window,
        "min_hits": min_hits,
        "drift_slow": drift_slow,
        "warn": warn,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    _save({"hits": hits, "steps": steps})
    return out

