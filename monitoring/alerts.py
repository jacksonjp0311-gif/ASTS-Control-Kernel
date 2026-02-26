import json
import os
from datetime import datetime

DEFAULT_THRESHOLDS = {
    "slow_drift_crit": 0.010,
    "slow_drift_warn": 0.006,
    "pressure_warn": 0.85,
    "divergence_warn": 0.60,
}

def _load_thresholds(root_dir):
    path = os.path.join(root_dir, "state", "thresholds.json")
    if not os.path.exists(path):
        return DEFAULT_THRESHOLDS

    # Use utf-8-sig so BOM never breaks system again
    with open(path, "r", encoding="utf-8-sig") as f:
        try:
            return json.load(f)
        except Exception:
            return DEFAULT_THRESHOLDS

def evaluate(theta, root_dir):

    th = _load_thresholds(root_dir)

    drift = theta.get("drift", {})
    if isinstance(drift, dict):
        drift_total = float(drift.get("total", 0.0))
        drift_fast  = float(drift.get("fast", 0.0))
        drift_slow  = float(drift.get("slow", 0.0))
    else:
        drift_total = float(drift)
        drift_fast  = 0.0
        drift_slow  = 0.0

    pressure   = float(theta.get("pressure", 0.0))
    divergence = float(theta.get("divergence", 0.0))

    level = "ok"
    warnings = []
    actions = []

    if drift_slow >= (th.get("slow_drift_crit", DEFAULT_THRESHOLDS["slow_drift_crit"])):
        level = "crit"
        warnings.append(f"SLOW_DRIFT_CRIT: {drift_slow:.6f}")
        actions += [
            "pause_or_slow_main_agent_decisions",
            "increase_consolidation",
            "capture_diagnostic_bundle"
        ]
    elif drift_slow >= (th.get("slow_drift_warn", DEFAULT_THRESHOLDS["slow_drift_warn"])):
        level = "warn"
        warnings.append(f"SLOW_DRIFT_WARN: {drift_slow:.6f}")
        actions += [
            "mark_uncertainty_high",
            "request_more_context"
        ]

    return {
        "level": level,
        "signals": {
            "drift_total": drift_total,
            "drift_fast": drift_fast,
            "drift_slow": drift_slow,
            "pressure": pressure,
            "divergence": divergence
        },
        "warnings": warnings,
        "actions": actions,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

