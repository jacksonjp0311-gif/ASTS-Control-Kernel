from adapters.openclaw.skill_entry import run_skill as base_skill
from control.governor_v2 import compute_execution_constraints_v2
from control.autostabilizer_v2 import stabilize_if_needed_v2

def run_skill(env: dict):
    # Call existing skill (telemetry-only core + monitoring)
    result = base_skill(env)

    theta = result.get("theta", {}) or {}
    drift = theta.get("drift", {}) or {}

    # Robust extraction
    drift_slow = 0.0
    drift_total = 0.0
    if isinstance(drift, dict):
        drift_slow = float(drift.get("slow", 0.0))
        drift_total = float(drift.get("total", 0.0))
    else:
        drift_total = float(drift or 0.0)

    step = 0
    try:
        step = int(env.get("step", 0))
    except Exception:
        step = 0

    constraints = compute_execution_constraints_v2(drift_slow, drift_total)
    env.update(constraints)

    # Stabilize with cooldown + cold reset of drift_state.json
    stabilization = stabilize_if_needed_v2(
        step=step,
        drift_slow=drift_slow,
        metrics=theta.get("metrics", {}),
        reset_threshold=0.015,
        cooldown_steps=5
    )

    if stabilization:
        print("🛠 V2 Auto-Stabilizer Triggered:", stabilization)

    print("⚙ V2 Adaptive Constraints:", constraints)

    return {
        **result,
        "constraints": constraints,
        "stabilization": stabilization
    }
