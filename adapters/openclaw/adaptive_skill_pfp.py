from adapters.openclaw.skill_entry import run_skill as base_skill
from stability.pfp.controller import apply_pfp

def run_skill(env):

    result = base_skill(env)

    theta = result.get("theta", {})
    step = int(env.get("step", 0))

    pfp = apply_pfp(step, theta)

    if pfp["pulse_event"]:
        print("⚡ PFP Pulse Triggered:", pfp["pulse_event"])

    print("📊 Drift Slow:", pfp["drift_slow"])
    print("📈 Predicted Drift:", pfp["predicted_drift"])

    return {
        **result,
        "pfp": pfp
    }
