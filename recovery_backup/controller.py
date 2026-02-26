import json
import os
from datetime import datetime
from typing import Dict, Any

from metrics.drift.drift import reset_baseline
from engine.recovery.plateau import push_and_check

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "state")
RECOVERY_STATE_FILE = os.path.join(STATE_DIR, "recovery_state.json")

DEFAULTS = {
    # Ladder
    "warn": 0.006,
    "crit": 0.010,
    "recover": 0.0115,
    "reset": 0.0125,

    # gates
    "cooldown_steps": 5,
    "max_backoff_steps": 3,

    # autonomous knobs
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
        return json.load(f)

def _save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def load_thresholds(root_dir: str) -> Dict[str, Any]:
    tpath = os.path.join(root_dir, "state", "thresholds.json")
    merged: Dict[str, Any] = dict(DEFAULTS)
    try:
        data = _load_json(tpath)
        if isinstance(data, dict):
            for k in merged.keys():
                if k in data:
                    merged[k] = data[k]
    except Exception:
        pass

    # clamp floats
    for k in ["warn","crit","recover","reset"]:
        merged[k] = _clamp01(merged.get(k, DEFAULTS[k]))

    # ints
    for k in ["cooldown_steps","max_backoff_steps","plateau_window","warn_streak_to_recover","crit_streak_to_reset","max_resets_per_100"]:
        try:
            merged[k] = int(merged.get(k, DEFAULTS[k]))
        except Exception:
            merged[k] = int(DEFAULTS[k])

    # floats
    for k in ["plateau_eps"]:
        try:
            merged[k] = float(merged.get(k, DEFAULTS[k]))
        except Exception:
            merged[k] = float(DEFAULTS[k])

    # bools
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
            "reset_events": []  # list of step indices, keep last 100
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
    # limit number of resets per rolling 100 steps
    events = [int(x) for x in (s.get("reset_events") or [])]
    k = int(s.get("k", 0))
    events = [e for e in events if (k - e) <= 100]
    s["reset_events"] = events
    return len(events) < int(th["max_resets_per_100"])

def decide(theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    th = load_thresholds(root_dir)
    s = _load_state()

    k = int(s["k"]) + 1
    s["k"] = k

    drift_slow = 0.0
    d = theta.get("drift", {})
    if isinstance(d, dict):
        try: drift_slow = float(d.get("slow", 0.0))
        except Exception: drift_slow = 0.0

    # base mode from ladder thresholds
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

    # plateau check: if we're stuck (span small) for window, escalate
    plateau = push_and_check(drift_slow, window=th["plateau_window"], eps=th["plateau_eps"])

    actions = []
    backoff_steps = 0

    reason = f"drift_slow={drift_slow:.6f} ladder(warn={th['warn']}, crit={th['crit']}, recover={th['recover']}, reset={th['reset']})"

    # gates
    can_reset_cooldown = (k - int(s.get("last_reset_k", -10**9))) >= int(th["cooldown_steps"])
    can_reset_rate = _rate_limit_ok(s, th)
    can_reset = can_reset_cooldown and can_reset_rate

    # autonomous escalation policy:
    # - if crit/recover persists crit_streak_to_reset -> reset (if enabled + gates)
    # - if warn persists warn_streak_to_recover or plateau -> recover behavior
    # - else follow base ladder
    if th["enable_autonomous_reset"]:
        if (int(s.get("crit_streak", 0)) >= int(th["crit_streak_to_reset"])) and can_reset:
            mode = "reset"
        elif (int(s.get("warn_streak", 0)) >= int(th["warn_streak_to_recover"])) or bool(plateau.get("plateau", False)):
            if mode == "warn":
                mode = "recover"

    if mode == "reset" and can_reset:
        actions.append("reset_baseline")
        s["last_reset_k"] = k
        s["backoff"] = 0
        ev = [int(x) for x in (s.get("reset_events") or [])]
        ev.append(k)
        s["reset_events"] = ev[-200:]
    elif mode in ("recover","crit","warn"):
        inc = 1 if mode in ("crit","recover") else 0
        s["backoff"] = min(int(s.get("backoff", 0)) + inc, int(th["max_backoff_steps"]))
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

    _save_state(s)

    return {
        "mode": (mode if (mode != "reset" or can_reset) else "recover"),
        "actions": actions,
        "backoff_steps": backoff_steps,
        "reason": reason + ("" if can_reset else " (reset gated)"),
        "plateau": plateau,
        "streaks": {"warn": int(s.get("warn_streak", 0)), "crit": int(s.get("crit_streak", 0))},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def apply(decision: Dict[str, Any], theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    # legacy compatibility: execute reset here if requested
    if "reset_baseline" in decision.get("actions", []):
        try:
            reset_baseline(theta.get("metrics", {}))
        except Exception:
            pass
    return decision
