import os
import sys

# --- PROJECT ROOT BOOTSTRAP (additive) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------------------------------
import json
import os
import time
from datetime import datetime

# This runner is additive: it does NOT depend on any adapter-side logging.
# It records whatever the skill returns (defensively) into a run file.

DEFAULT_STEPS = int(os.environ.get("PFP_STEPS", "25"))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS_DIR = os.path.join(ROOT, "benchmarks", "runs")
os.makedirs(RUNS_DIR, exist_ok=True)

def _now_tag() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _safe_get_drift(theta: dict) -> dict:
    d = theta.get("drift", {})
    if isinstance(d, dict):
        return {
            "total": float(d.get("total", 0.0)),
            "fast":  float(d.get("fast", 0.0)),
            "slow":  float(d.get("slow", 0.0)),
        }
    # fallback: scalar drift
    try:
        return {"total": float(d), "fast": 0.0, "slow": 0.0}
    except Exception:
        return {"total": 0.0, "fast": 0.0, "slow": 0.0}

def main(steps: int = DEFAULT_STEPS) -> str:
    from adapters.openclaw.adaptive_skill_pfp import run_skill

    run_path = os.path.join(RUNS_DIR, f"pfp_run_{_now_tag()}.jsonl")

    print(f"Running PFP benchmark... steps={steps}")
    print(f"Writing: {run_path}")

    last_V = None
    pulse_count = 0

    with open(run_path, "a", encoding="utf-8") as f:
        for k in range(steps):
            env = {"step": k}
            out = run_skill(env)  # expected: {"theta":..., "pfp":..., ...}

            theta = out.get("theta", {})
            pfp = out.get("pfp", {}) if isinstance(out.get("pfp", {}), dict) else {}

            drift = _safe_get_drift(theta)
            drift_slow = drift["slow"]
            V = float(drift_slow) ** 2

            # Coast delta-V proxy (between steps)
            delta_V_coast = None
            if last_V is not None:
                delta_V_coast = V - last_V

            # Pulse info (if any)
            pulse_event = pfp.get("pulse_event", None)
            if pulse_event:
                pulse_count += 1

            # If adapter provided these, keep them; otherwise None
            predicted = pfp.get("predicted_drift", pfp.get("predicted", None))
            delta_V_pulse = None
            V_before = None
            V_after = None
            contraction_verified = None

            if isinstance(pulse_event, dict):
                # Prefer explicit values if adapter wrote them
                V_before = pulse_event.get("V_before", None)
                V_after  = pulse_event.get("V_after", None)
                delta_V_pulse = pulse_event.get("delta_V_pulse", None)

            # If pulse is present but adapter didn't compute delta_V_pulse,
            # we can't infer it safely without knowing its internal alpha.
            # So we only mark "verified" if explicit.
            if delta_V_pulse is not None and delta_V_coast is not None:
                try:
                    contraction_verified = (float(delta_V_pulse) < float(delta_V_coast))
                except Exception:
                    contraction_verified = None

            rec = {
                "ts_utc": datetime.utcnow().isoformat() + "Z",
                "step": k,

                "drift_total": drift["total"],
                "drift_fast": drift["fast"],
                "drift_slow": drift["slow"],
                "V": V,

                "delta_V_coast": delta_V_coast,

                "pulse_event": pulse_event,
                "predicted": predicted,

                # pulse/verification fields (may be null)
                "V_before": V_before,
                "V_after": V_after,
                "delta_V_pulse": delta_V_pulse,
                "contraction_verified": contraction_verified,
            }

            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()

            last_V = V

            print(f"STEP {k:02d} | drift_slow={drift_slow:.6f} | V={V:.8f} | pulse={'Y' if pulse_event else 'n'}")
            time.sleep(0.01)

    print(f"Done. pulses={pulse_count}")
    print(f"Run file: {run_path}")
    return run_path

if __name__ == "__main__":
    main()
