import os, sys, json, time, statistics
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from adapters.openclaw.adaptive_skill_pfp import run_skill

STEPS = 40

def now():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


# --- PROJECT_ROOT_OUTPUT_FIX ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RUN_BASE = os.path.join(PROJECT_ROOT, "tests", "stress", "runs")
os.makedirs(RUN_BASE, exist_ok=True)
# --------------------------------

def run_stress(alpha=None, drift_mult=1.0, threshold_mult=1.0, label="stress"):
    ts = now()
    run_path = os.path.join(RUN_BASE, f"{label}_{ts}.jsonl")

    print(f"Running stress: alpha={alpha}, drift_mult={drift_mult}, threshold_mult={threshold_mult}")
    print("Writing:", run_path)

    margin_fail = False
    pulse_margins = []

    with open(run_path,"w") as f:
        prev_V = None

        for step in range(STEPS):
            payload = {"step":step}

            if alpha is not None:
                payload["alpha_override"] = alpha

            out = run_skill(payload)

            drift = out.get("theta",{}).get("drift",{})
            slow = float(drift.get("slow",0.0)) * drift_mult

            threshold = out.get("pfp",{}).get("D_MAX",0.01) * threshold_mult
            V = slow**2

            delta_coast = None
            if prev_V is not None:
                delta_coast = V - prev_V

            pulse = out.get("pfp",{}).get("pulse_event")
            delta_pulse = None

            if pulse and "delta_V_pulse" in pulse:
                delta_pulse = pulse["delta_V_pulse"]
                if delta_coast is not None and abs(delta_coast) > 1e-12:
                    margin = abs(delta_pulse)/abs(delta_coast)
                    pulse_margins.append(margin)
                    if margin < 1:
                        margin_fail = True

            record = {
                "step":step,
                "drift_slow":slow,
                "V":V,
                "delta_V_coast":delta_coast,
                "pulse":pulse
            }

            f.write(json.dumps(record)+"\n")
            prev_V = V
            time.sleep(0.01)

    summary = {
        "alpha":alpha,
        "drift_mult":drift_mult,
        "threshold_mult":threshold_mult,
        "margin_fail":margin_fail,
        "margin_mean":statistics.mean(pulse_margins) if pulse_margins else None,
        "margin_min":min(pulse_margins) if pulse_margins else None
    }

    print("Summary:", summary)
    return summary

