import json
import os
from datetime import datetime
from typing import Dict, Any

from metrics.drift.drift import reset_baseline

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "state")
RECOVERY_STATE_FILE = os.path.join(STATE_DIR, "recovery_state.json")

DEFAULTS = {
    # Ladder: warn -> crit -> recover -> reset
    "warn": 0.006,
    "crit": 0.010,
    "recover": 0.0115,   # <— critical fix: closes dead-zone between crit and reset
    "reset": 0.0125,     # baseline reset trigger
    "cooldown_steps": 5, # don't reset repeatedly
    "max_backoff_steps": 3
}

def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))

def _load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def load_thresholds(root_dir: str) -> Dict[str, float]:
    # Merge thresholds.json (optional) with defaults
    tpath = os.path.join(root_dir, "state", "thresholds.json")
    merged = DEFAULTS.copy()
    try:
        data = _load_json(tpath)
        if isinstance(data, dict):
            for k in merged.keys():
                if k in data:
                    merged[k] = float(data[k])
    except Exception:
        pass
    # clamp
    for k in ["warn","crit","recover","reset"]:
        merged[k] = _clamp01(merged.get(k, DEFAULTS[k]))
    merged["cooldown_steps"] = int(merged.get("cooldown_steps", DEFAULTS["cooldown_steps"]))
    merged["max_backoff_steps"] = int(merged.get("max_backoff_steps", DEFAULTS["max_backoff_steps"]))
    return merged

def _load_state() -> Dict[str, Any]:
    s = _load_json(RECOVERY_STATE_FILE)
    if not isinstance(s, dict):
        return {"k": 0, "last_reset_k": -10**9, "backoff": 0}
    return {
        "k": int(s.get("k", 0)),
        "last_reset_k": int(s.get("last_reset_k", -10**9)),
        "backoff": int(s.get("backoff", 0))
    }

def _save_state(s: Dict[str, Any]) -> None:
    _save_json(RECOVERY_STATE_FILE, s)

def decide(theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    """
    Returns recovery decision:
      {
        "mode": "ok"|"warn"|"crit"|"recover"|"reset",
        "actions": [...],
        "backoff_steps": int,
        "reason": str,
        "timestamp": iso
      }
    """
    th = load_thresholds(root_dir)
    s = _load_state()
    k = int(s["k"]) + 1
    s["k"] = k

    drift_slow = 0.0
    drift_total = 0.0
    d = theta.get("drift", {})
    if isinstance(d, dict):
        drift_slow = float(d.get("slow", 0.0))
        drift_total = float(d.get("total", 0.0))

    # Determine mode
    mode = "ok"
    if drift_slow >= th["reset"]:
        mode = "reset"
    elif drift_slow >= th["recover"]:
        mode = "recover"
    elif drift_slow >= th["crit"]:
        mode = "crit"
    elif drift_slow >= th["warn"]:
        mode = "warn"

    actions = []
    backoff_steps = 0
    reason = f"drift_slow={drift_slow:.6f} thresholds(warn={th['warn']}, crit={th['crit']}, recover={th['recover']}, reset={th['reset']})"

    # Cooldown gate for reset
    can_reset = (k - int(s.get("last_reset_k", -10**9))) >= th["cooldown_steps"]

    if mode == "reset" and can_reset:
        actions.append("reset_baseline")
        s["last_reset_k"] = k
        s["backoff"] = 0
    elif mode in ("recover","crit","warn"):
        # escalate backoff gently; cap
        s["backoff"] = min(int(s.get("backoff", 0)) + (1 if mode in ("crit","recover") else 0), th["max_backoff_steps"])
        backoff_steps = int(s["backoff"])
        if mode == "recover":
            actions += ["tighten_constraints", "request_validation", "consider_reset_next"]
        elif mode == "crit":
            actions += ["tighten_constraints", "request_validation"]
        elif mode == "warn":
            actions += ["mark_uncertainty_high"]

    _save_state(s)

    return {
        "mode": mode if (mode != "reset" or can_reset) else "recover",
        "actions": actions,
        "backoff_steps": backoff_steps,
        "reason": reason + ("" if can_reset else " (reset cooldown active)"),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def apply(decision: Dict[str, Any], theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    """
    Applies recovery actions (safe side-effects):
    - reset baseline metrics (drift)
    Returns updated bundle.
    """
    if "reset_baseline" in decision.get("actions", []):
        metrics = theta.get("metrics", {})
        try:
            reset_baseline(metrics)
        except Exception:
            pass
    return decision
