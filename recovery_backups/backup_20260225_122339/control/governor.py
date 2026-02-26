def compute_execution_constraints(drift_slow: float):
    drift_slow = float(drift_slow or 0.0)

    # Smooth degradation instead of step jumps
    max_depth = max(1, int(3 - drift_slow * 20))

    risk_mode = "normal"
    if drift_slow >= 0.010:
        risk_mode = "restricted"
    elif drift_slow >= 0.006:
        risk_mode = "cautious"

    return {
        "risk_mode": risk_mode,
        "max_depth": max_depth,
        "require_validation": drift_slow >= 0.006,
    }
