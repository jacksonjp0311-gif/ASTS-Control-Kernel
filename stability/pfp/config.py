import os, json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
THRESHOLDS_FILE = os.path.join(ROOT_DIR, "state", "thresholds.json")

DEFAULTS = {
    "slow_drift_crit": 0.010,
    "slow_drift_warn": 0.006,
    "pfp_dmax": None,         # if None -> uses slow_drift_crit
    "pfp_cooldown_steps": 5
}

def load_thresholds():
    data = {}
    if os.path.exists(THRESHOLDS_FILE):
        try:
            with open(THRESHOLDS_FILE, "r", encoding="utf-8-sig") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}

    merged = DEFAULTS.copy()
    merged.update(data)

    # Decide Dmax:
    # - If pfp_dmax explicitly set, use it
    # - Else align with slow_drift_crit
    dmax = merged.get("pfp_dmax", None)
    if dmax is None:
        dmax = merged.get("slow_drift_crit", DEFAULTS["slow_drift_crit"])
    try:
        dmax = float(dmax)
    except Exception:
        dmax = float(DEFAULTS["slow_drift_crit"])

    try:
        cooldown = int(merged.get("pfp_cooldown_steps", DEFAULTS["pfp_cooldown_steps"]))
    except Exception:
        cooldown = int(DEFAULTS["pfp_cooldown_steps"])

    return {
        "dmax": dmax,
        "cooldown_steps": max(0, cooldown),
        "raw": merged
    }
