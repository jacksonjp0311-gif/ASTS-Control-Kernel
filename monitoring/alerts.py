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

    pressure = _optional_unit(theta.get("pressure"))
    divergence = _optional_unit(theta.get("divergence"))

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

    # Witnesses may raise warn. They never promote crit or reset.
    pressure_warn = float(th.get("pressure_warn", DEFAULT_THRESHOLDS["pressure_warn"]))
    divergence_warn = float(th.get("divergence_warn", DEFAULT_THRESHOLDS["divergence_warn"]))
    if pressure is not None and pressure >= pressure_warn:
        warnings.append(f"PRESSURE_WARN: {pressure:.6f}")
        if level == "ok":
            level = "warn"
            actions += ["mark_uncertainty_high"]
    if divergence is not None and divergence >= divergence_warn:
        warnings.append(f"DIVERGENCE_WARN: {divergence:.6f}")
        if level == "ok":
            level = "warn"
            actions += ["request_more_context"]

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


def _optional_unit(value):
    if value is None:
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, x))

