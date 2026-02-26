from engine.execution.runner import run_step

def run_skill(env):
    theta, monitor_bundle = run_step(env)

    # Correct level extraction:
    assessment = monitor_bundle.get("assessment", {}) if isinstance(monitor_bundle, dict) else {}
    level = assessment.get("level") or monitor_bundle.get("status") or "ok"

    signals = assessment.get("signals", {}) if isinstance(assessment, dict) else {}
    drift_slow = float(signals.get("drift_slow", 0.0) or 0.0)

    if level == "crit":
        mode = "restricted"
        env["risk_mode"] = "restricted"
        env["max_depth"] = 1
        env["require_validation"] = True
    elif level == "warn":
        mode = "cautious"
        env["risk_mode"] = "cautious"
        env["max_depth"] = 2
        env["require_validation"] = True
    else:
        mode = "normal"
        env["risk_mode"] = "normal"
        env["max_depth"] = 3
        env["require_validation"] = False

    env["drift_slow"] = drift_slow

    print("🧠 OpenClaw Mode:", mode)
    print("   Drift Slow:", drift_slow)

    return {
        "theta": theta,
        "mode": mode,
        "level": level,
        "drift_slow": drift_slow,
        "recommended_actions": assessment.get("actions", []),
        "warnings": assessment.get("warnings", []),
    }
