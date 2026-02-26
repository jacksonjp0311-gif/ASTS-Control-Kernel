import os
from monitoring.alerts import evaluate

def monitor(theta):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assessment = evaluate(theta, root_dir)

    print("------ TELEMETRY ------")
    print("Metrics:", theta.get("metrics", {}))

    d = theta.get("drift", {})
    if isinstance(d, dict):
        print("Drift(total):", d.get("total"))
        print("Drift(fast): ", d.get("fast"))
        print("Drift(slow): ", d.get("slow"))
    else:
        print("Drift(total):", d)

    print("Divergence:", theta.get("divergence"))
    print("Pressure:", theta.get("pressure"))
    print("Hash:", theta.get("hash", "")[:12])
    print("-----------------------")

    if assessment["level"] == "warn":
        print("🟡 WARNING TRIGGERED")
        for w in assessment["warnings"]:
            print(" -", w)

    if assessment["level"] == "crit":
        print("🔴 CRITICAL STABILITY EVENT")
        for w in assessment["warnings"]:
            print(" -", w)
        print("Recommended actions:")
        for a in assessment["actions"]:
            print("  •", a)

    return {
        "status": assessment["level"],
        "assessment": assessment
    }
