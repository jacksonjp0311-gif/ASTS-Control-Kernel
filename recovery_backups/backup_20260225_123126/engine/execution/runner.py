from engine.recovery.persist import persist_over
from engine.recovery.plateau import check as plateau_check
from engine.recovery.controller import decide, apply
from runtime.observers.base import run_observers
import os

from runtime.telemetry_field.aggregator import aggregate
from ledger.ledger import append_entry
from monitoring.monitor import monitor
import os
from engine.recovery.controller import decide, apply


def run_step(env):
    reports = run_observers(env)
    theta = aggregate(reports)

    m = monitor(theta)
    # --- Active recovery (persistence reset) ---
    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        th_path = os.path.join(root_dir, "state", "thresholds.json")
        import json
        th = json.load(open(th_path, "r", encoding="utf-8"))
        crit = float(th.get("slow_drift_crit", 0.015))
        steps = int(th.get("persist_steps", 3))

        drift_slow = 0.0
        d = theta.get("drift", {})
        if isinstance(d, dict):
            drift_slow = float(d.get("slow", 0.0))

        if persist_over(drift_slow, crit, steps):
            print("🟢 PERSISTENCE RESET: drift_slow stayed >= crit for", steps, "steps")
            from metrics.drift.drift import reset_baseline
            reset_baseline(theta.get("metrics", {}))
    except Exception:
        pass

    # --- Structured recovery decision (ledger-visible) ---
    try:
        decision = decide(theta, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
        decision = apply(decision, theta, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    except Exception:
        decision = {"mode":"error","actions":[]}
    # Recovery controller (bounded stabilization)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    

    # Optional backoff (telemetry-only behavior)
    # Caller may choose to sleep/backoff based on decision["backoff_steps"]


    # Append-only ledger event
    append_entry({
        "type": "STEP",
        "step": env.get("step"),
        "theta": theta,
        "monitoring": {
            "status": m.get("status"),
            "level": m.get("level"),
            "assessment": m.get("assessment"),
        },
        "recovery": decision,
    })

    return theta, m

def run_session(steps=10):
    print("Starting ASTS session...")
    for k in range(steps):
        print(f"\\nSTEP {k+1}")
        env = {"step": k}
        run_step(env)
    print("\\nSession complete.")

if __name__ == "__main__":
    run_session()










