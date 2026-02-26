def execute_recovery(decision, drift_state):
    if decision["mode"] == "hard_reset":
        drift_state["slow"] = 0.0
        drift_state["fast"] = 0.0
        print("🟢 HARD RESET APPLIED")

    elif decision["mode"] == "baseline_reset":
        drift_state["slow"] *= 0.5
        print("🟡 BASELINE RESET")

    elif decision["mode"] == "consolidate":
        print("🔵 CONSOLIDATION STEP")

    return drift_state
