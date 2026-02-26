import json
import os
from datetime import datetime
from typing import Dict, Any

from metrics.drift.drift import reset_baseline

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "state")
RECOVERY_STATE_FILE = os.path.join(STATE_DIR, "recovery_state.json")

DEFAULTS = {
    "warn": 0.006,
    "crit": 0.010,
    "recover": 0.0115,
    "reset": 0.0125,

    "cooldown_steps": 5,
    "max_backoff_steps": 3,

    "plateau_window": 6,
    "plateau_eps": 0.00015,

    "warn_streak_to_recover": 6,
    "crit_streak_to_reset": 3,
    "max_resets_per_100": 3,

    "enable_autonomous_reset": True,
    "verbose_recovery": True
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
    with open(path, "r", encoding="utf-8-sig") as f:
        try:
            return json.load(f)
        except Exception:
            return None

def _save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def load_thresholds(root_dir: str) -> Dict[str, Any]:
    tpath = os.path.join(root_dir, "state", "thresholds.json")
    merged: Dict[str, Any] = dict(DEFAULTS)

    data = _load_json(tpath)
    if isinstance(data, dict):
        for k in merged.keys():
            if k in data:
                merged[k] = data[k]

    for k in ["warn", "crit", "recover", "reset"]:
        merged[k] = _clamp01(merged.get(k, DEFAULTS[k]))

    for k in ["cooldown_steps","max_backoff_steps","plateau_window","warn_streak_to_recover","crit_streak_to_reset","max_resets_per_100"]:
        try:
            merged[k] = int(merged.get(k, DEFAULTS[k]))
        except Exception:
            merged[k] = int(DEFAULTS[k])

    try:
        merged["plateau_eps"] = float(merged.get("plateau_eps", DEFAULTS["plateau_eps"]))
    except Exception:
        merged["plateau_eps"] = float(DEFAULTS["plateau_eps"])

    merged["enable_autonomous_reset"] = bool(merged.get("enable_autonomous_reset", True))
    merged["verbose_recovery"] = bool(merged.get("verbose_recovery", True))

    return merged

def _load_state() -> Dict[str, Any]:
    s = _load_json(RECOVERY_STATE_FILE)
    if not isinstance(s, dict):
        return {
            "k": 0,
            "last_reset_k": -10**9,
            "backoff": 0,
            "warn_streak": 0,
            "crit_streak": 0,
            "reset_events": []
        }
    return {
        "k": int(s.get("k", 0)),
        "last_reset_k": int(s.get("last_reset_k", -10**9)),
        "backoff": int(s.get("backoff", 0)),
        "warn_streak": int(s.get("warn_streak", 0)),
        "crit_streak": int(s.get("crit_streak", 0)),
        "reset_events": list(s.get("reset_events", []))[:200]
    }

def _save_state(s: Dict[str, Any]) -> None:
    _save_json(RECOVERY_STATE_FILE, s)

def _rate_limit_ok(s: Dict[str, Any], th: Dict[str, Any]) -> bool:
    events = [int(x) for x in (s.get("reset_events") or [])]
    k = int(s.get("k", 0))
    events = [e for e in events if (k - e) <= 100]
    s["reset_events"] = events
    return len(events) < int(th["max_resets_per_100"])

def _plateau_check(drift_slow: float, root_dir: str, window: int, eps: float) -> Dict[str, Any]:
    # Optional plateau module; if missing, we degrade gracefully.
    try:
        from engine.recovery.plateau import check as plateau_check
        out = plateau_check({"drift":{"slow":drift_slow}}, root_dir)
        if isinstance(out, dict):
            return out
    except Exception:
        pass
    return {"plateau": False, "span": None, "mean": float(drift_slow)}

def decide(theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    th = load_thresholds(root_dir)
    s = _load_state()

    k = int(s["k"]) + 1
    s["k"] = k

    drift_slow = 0.0
    d = theta.get("drift", {})
    if isinstance(d, dict):
        try:
            drift_slow = float(d.get("slow", 0.0))
        except Exception:
            drift_slow = 0.0

    # base ladder
    mode = "ok"
    if drift_slow >= th["reset"]:
        mode = "reset"
    elif drift_slow >= th["recover"]:
        mode = "recover"
    elif drift_slow >= th["crit"]:
        mode = "crit"
    elif drift_slow >= th["warn"]:
        mode = "warn"

    # streak tracking
    if mode == "warn":
        s["warn_streak"] = int(s.get("warn_streak", 0)) + 1
        s["crit_streak"] = 0
    elif mode in ("crit","recover","reset"):
        s["crit_streak"] = int(s.get("crit_streak", 0)) + 1
        s["warn_streak"] = 0
    else:
        s["warn_streak"] = 0
        s["crit_streak"] = 0

    plateau = _plateau_check(drift_slow, root_dir, window=th["plateau_window"], eps=th["plateau_eps"])

    actions = []
    backoff_steps = 0
    reason = f"drift_slow={drift_slow:.6f} ladder(warn={th['warn']}, crit={th['crit']}, recover={th['recover']}, reset={th['reset']})"

    # gates
    can_reset_cooldown = (k - int(s.get("last_reset_k", -10**9))) >= int(th["cooldown_steps"])
    can_reset_rate = _rate_limit_ok(s, th)
    can_reset = can_reset_cooldown and can_reset_rate

    # autonomous escalation
    if th["enable_autonomous_reset"]:
        if (int(s.get("crit_streak", 0)) >= int(th["crit_streak_to_reset"])) and can_reset:
            mode = "reset"
        elif (int(s.get("warn_streak", 0)) >= int(th["warn_streak_to_recover"])) or bool(plateau.get("plateau", False)):
            if mode == "warn":
                mode = "recover"

    # actions + backoff policy (+decay)
    if mode == "reset" and can_reset:
        actions.append("reset_baseline")
        s["last_reset_k"] = k
        s["backoff"] = 0
        ev = [int(x) for x in (s.get("reset_events") or [])]
        ev.append(k)
        s["reset_events"] = ev[-200:]
    elif mode in ("recover","crit","warn"):
        if mode in ("recover","crit"):
            s["backoff"] = min(int(s.get("backoff", 0)) + 1, int(th["max_backoff_steps"]))
        else:
            # decay on warn so it doesn't stay pegged
            s["backoff"] = max(0, int(s.get("backoff", 0)) - 1)

        backoff_steps = int(s["backoff"])

        if mode == "recover":
            actions += ["tighten_constraints", "request_validation"]
            if bool(plateau.get("plateau", False)):
                actions += ["plateau_detected"]
            if (int(s.get("crit_streak", 0)) >= int(th["crit_streak_to_reset"])) and (not can_reset):
                actions += ["reset_blocked_by_gate"]
        elif mode == "crit":
            actions += ["tighten_constraints", "request_validation"]
        elif mode == "warn":
            actions += ["mark_uncertainty_high"]
    else:
        # ok: decay harder
        s["backoff"] = max(0, int(s.get("backoff", 0)) - 2)
        backoff_steps = int(s["backoff"])

    _save_state(s)

    # if reset is gated, downgrade to recover semantics (but preserve reason)
    out_mode = (mode if (mode != "reset" or can_reset) else "recover")
    return {
        "mode": out_mode,
        "actions": actions,
        "backoff_steps": backoff_steps,
        "reason": reason + ("" if can_reset else " (reset gated)"),
        "plateau": plateau,
        "streaks": {"warn": int(s.get("warn_streak", 0)), "crit": int(s.get("crit_streak", 0))},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def apply(decision: Dict[str, Any], theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    # legacy compatibility: if controller requests baseline reset, do it here too
    if "reset_baseline" in (decision.get("actions", []) or []):
        try:
            reset_baseline(theta.get("metrics", {}) or {})
        except Exception:
            pass
    return decision
