from adapters.openclaw.skill_entry import run_skill as base_skill
from control.governor import compute_execution_constraints
from control.autostabilizer import stabilize_if_needed

def run_skill(env):
    result = base_skill(env)

    drift_slow = result.get("drift_slow", 0.0)
    theta = result.get("theta", {})

    constraints = compute_execution_constraints(drift_slow)

    env.update(constraints)

    stabilization = stabilize_if_needed(
        drift_slow,
        theta.get("metrics", {})
    )

    if stabilization:
        print("🛠 Auto-Stabilizer Triggered:", stabilization)

    print("⚙ Adaptive Constraints:", constraints)

    return {
        **result,
        "constraints": constraints,
        "stabilization": stabilization
    }
