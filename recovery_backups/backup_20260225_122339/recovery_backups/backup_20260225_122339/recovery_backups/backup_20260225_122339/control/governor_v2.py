def compute_execution_constraints_v2(drift_slow: float, drift_total: float = 0.0):
    drift_slow = float(drift_slow or 0.0)
    drift_total = float(drift_total or 0.0)

    # Smoother depth schedule: drops with slow drift, but never below 1
    max_depth = max(1, int(round(4 - (drift_slow * 30))))

    # Mode boundaries (aligned to your thresholds.json defaults)
    if drift_slow >= 0.010:
        risk_mode = "restricted"
        require_validation = True
    elif drift_slow >= 0.006:
        risk_mode = "cautious"
        require_validation = True
    else:
        risk_mode = "normal"
        require_validation = False

    return {
        "risk_mode": risk_mode,
        "max_depth": max_depth,
        "require_validation": require_validation,
        "drift_slow": drift_slow,
        "drift_total": drift_total,
    }
