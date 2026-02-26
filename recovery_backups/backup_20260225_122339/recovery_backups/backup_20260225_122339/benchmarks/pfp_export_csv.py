import os
import sys

# --- PROJECT ROOT BOOTSTRAP (additive) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------------------------------
import csv
import glob
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

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
                continue
    return out

def main():
    import sys
    run_path = sys.argv[1] if len(sys.argv) > 1 else _latest_run()
    if not run_path or not os.path.exists(run_path):
        raise SystemExit("No run file found. Run: python benchmarks/run_pfp_benchmark.py")

    rows = _read_jsonl(run_path)
    out_csv = os.path.join(REPORTS_DIR, f"pfp_phase_{_now_tag()}.csv")

    fields = [
        "step",
        "drift_slow",
        "V",
        "delta_V_coast",
        "delta_V_pulse",
        "contraction_verified",
        "pulse_event",
        "predicted",
        "ts_utc",
    ]

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, None) for k in fields})

    print(f"Wrote CSV: {out_csv}")

if __name__ == "__main__":
    main()
