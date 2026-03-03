from engine.recovery.persist import persist_over
from engine.recovery.plateau import check as plateau_check
from stability.pfp.controller import decide, apply
from engine.recovery.executor import execute

from runtime.observers.base import run_observers
from runtime.telemetry_field.aggregator import aggregate
from monitoring.monitor import monitor
from ledger.ledger import append_entry

import os
import json


def _root_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_thresholds(root_dir: str) -> dict:
    path = os.path.join(root_dir, "state", "thresholds.json")
    if not os.path.exists(path):
        return {}
    # utf-8-sig prevents BOM issues
    with open(path, "r", encoding="utf-8-sig") as f:
        try:
            x = json.load(f)
            return x if isinstance(x, dict) else {}
        except Exception:
            return {}


def run_step(env: dict):
    # 1) Observe + aggregate
    reports = run_observers(env)
    theta = aggregate(reports)

    # 2) Monitor (prints telemetry + returns assessment bundle)
    m = monitor(theta)

    root_dir = _root_dir()
    th = _load_thresholds(root_dir)

    # 3) Plateau sensing (if module exists / meaningful)
    plateau = {}
    try:
        plateau = plateau_check(theta, root_dir)  # may return dict
        if plateau is None:
            plateau = {}
    except Exception:
        plateau = {}

    # 4) Persistence reset (bounded, deterministic)
    try:
        crit  = float(th.get("slow_drift_crit", 0.010))
        steps = int(th.get("persist_steps", 3))

        d = theta.get("drift", {})
        drift_slow = float(d.get("slow", 0.0)) if isinstance(d, dict) else 0.0

        if persist_over(drift_slow, crit, steps):
            print("🟢 PERSISTENCE RESET: drift_slow >= crit for", steps, "steps")
            from metrics.drift.drift import reset_baseline
            reset_baseline(theta.get("metrics", {}))
    except Exception:
        pass

    # 5) Structured recovery decision + execution (single source of truth)
    try:
        decision = decide(theta, root_dir)
        decision = apply(decision, theta, root_dir)
        decision = execute(decision, theta, root_dir)
    except Exception:
        decision = {"mode": "error", "actions": [], "backoff_steps": 0, "reason": "exception_in_recovery"}

    # 6) Optional: verbose recovery print (controlled by thresholds.json)
    try:
        if bool(th.get("verbose_recovery", True)):
            mode = decision.get("mode")
            if mode and mode != "ok":
                print(f"🛠️  RECOVERY: mode={mode} backoff={decision.get('backoff_steps', 0)}")
                acts = decision.get("actions", [])
                if acts:
                    for a in acts:
                        print("  ↳", a)
    except Exception:
        pass

    # 7) Append-only ledger event
    append_entry({
        "type": "STEP",
        "step": env.get("step"),
        "theta": theta,
        "monitoring": {
            "status": m.get("status"),
            "assessment": m.get("assessment"),
        },
        "recovery": decision,
        "plateau": plateau,
    })

    return theta, m, decision


def run_session(steps: int = 10):
    print("Starting ASTS session...")
    for k in range(int(steps)):
        print(f"\\nSTEP {k+1}")
        env = {"step": k}
        run_step(env)
    print("\\nSession complete.")


if __name__ == "__main__":
    run_session()

