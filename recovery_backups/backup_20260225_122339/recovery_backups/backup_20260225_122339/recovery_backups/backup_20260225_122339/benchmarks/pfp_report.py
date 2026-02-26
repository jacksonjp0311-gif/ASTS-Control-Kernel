import os
import sys

# --- PROJECT ROOT BOOTSTRAP (additive) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------------------------------
import glob
import json
import os
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS_DIR = os.path.join(ROOT, "benchmarks", "runs")
REPORTS_DIR = os.path.join(ROOT, "benchmarks", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def _now_tag() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _latest_run() -> Optional[str]:
    pats = sorted(glob.glob(os.path.join(RUNS_DIR, "pfp_run_*.jsonl")))
    return pats[-1] if pats else None

def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # keep going; corrupt line shouldn't kill analysis
                continue
    return out

def _mean(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None

def _stdev(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return statistics.pstdev(xs) if len(xs) >= 2 else None

def analyze(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(records)
    pulses = [r for r in records if r.get("pulse_event")]
    pulse_n = len(pulses)

    drift_slow = [float(r.get("drift_slow", 0.0)) for r in records]
    V = [float(r.get("V", 0.0)) for r in records]

    dV_coast_all = []
    for r in records:
        v = r.get("delta_V_coast", None)
        if v is None:
            continue
        try:
            dV_coast_all.append(float(v))
        except Exception:
            pass

    dV_pulse = []
    verified = 0
    verified_total = 0
    margins = []  # |dV_pulse| / |dV_coast| when both available

    for r in records:
        if not r.get("pulse_event"):
            continue

        dvp = r.get("delta_V_pulse", None)
        dvc = r.get("delta_V_coast", None)

        if dvp is not None:
            try:
                dV_pulse.append(float(dvp))
            except Exception:
                pass

        cv = r.get("contraction_verified", None)
        if cv is not None:
            verified_total += 1
            if bool(cv):
                verified += 1

        if dvp is not None and dvc is not None:
            try:
                dvp_f = float(dvp)
                dvc_f = float(dvc)
                if dvc_f != 0.0:
                    margins.append(abs(dvp_f) / abs(dvc_f))
            except Exception:
                pass

    report = {
        "summary": {
            "records": n,
            "pulses": pulse_n,
            "pulses_per_step": (pulse_n / n) if n else None,

            "drift_slow_mean": _mean(drift_slow),
            "drift_slow_max": max(drift_slow) if drift_slow else None,
            "drift_slow_stdev": _stdev(drift_slow),

            "V_mean": _mean(V),
            "V_max": max(V) if V else None,

            "delta_V_coast_mean": _mean(dV_coast_all),
            "delta_V_coast_stdev": _stdev(dV_coast_all),

            "delta_V_pulse_mean": _mean(dV_pulse),
            "delta_V_pulse_min": min(dV_pulse) if dV_pulse else None,

            "contraction_verified_count": verified,
            "contraction_verified_total": verified_total,
            "contraction_verified_rate": (verified / verified_total) if verified_total else None,

            "contraction_margin_mean_abs_ratio": _mean(margins),
            "contraction_margin_max_abs_ratio": max(margins) if margins else None,
        },
        "notes": [
            "V proxy uses V = drift_slow^2.",
            "delta_V_coast is step-to-step V difference (V_k - V_{k-1}).",
            "delta_V_pulse / verified fields are only present if adapter emits them; otherwise null.",
        ],
    }
    return report

def write_report(report: Dict[str, Any], source_path: str) -> str:
    out_path = os.path.join(REPORTS_DIR, f"pfp_report_{_now_tag()}.json")
    payload = {
        "ts_utc": datetime.utcnow().isoformat() + "Z",
        "source_run": os.path.abspath(source_path),
        **report,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return out_path

def print_human(report: Dict[str, Any]) -> None:
    s = report["summary"]
    print("====================================")
    print("PFP BENCHMARK REPORT")
    print("====================================")
    print(f"steps:            {s['records']}")
    print(f"pulses:           {s['pulses']}  (rate={s['pulses_per_step']})")
    print("")
    print(f"drift_slow mean:  {s['drift_slow_mean']}")
    print(f"drift_slow max:   {s['drift_slow_max']}")
    print(f"drift_slow stdev: {s['drift_slow_stdev']}")
    print("")
    print(f"V mean:           {s['V_mean']}")
    print(f"V max:            {s['V_max']}")
    print("")
    print(f"Î”V_coast mean:    {s['delta_V_coast_mean']}")
    print(f"Î”V_coast stdev:   {s['delta_V_coast_stdev']}")
    print("")
    print(f"Î”V_pulse mean:    {s['delta_V_pulse_mean']}")
    print(f"Î”V_pulse min:     {s['delta_V_pulse_min']}")
    print("")
    print(f"verified:         {s['contraction_verified_count']} / {s['contraction_verified_total']} (rate={s['contraction_verified_rate']})")
    print(f"margin |Î”Vp|/|Î”Vc| mean: {s['contraction_margin_mean_abs_ratio']}")
    print(f"margin |Î”Vp|/|Î”Vc| max:  {s['contraction_margin_max_abs_ratio']}")
    print("====================================")

def main():
    import sys
    run_path = sys.argv[1] if len(sys.argv) > 1 else _latest_run()
    if not run_path or not os.path.exists(run_path):
        raise SystemExit("No run file found. Run: python benchmarks/run_pfp_benchmark.py")

    records = _read_jsonl(run_path)
    rep = analyze(records)
    print_human(rep)
    out_path = write_report(rep, run_path)
    print("")
    print(f"Wrote report: {out_path}")

if __name__ == "__main__":
    main()
