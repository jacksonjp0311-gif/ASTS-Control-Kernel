import os
import json
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BENCH_DIR = os.path.join(ROOT_DIR, "benchmarks")
LOG_FILE = os.path.join(BENCH_DIR, "pfp_runs.jsonl")

os.makedirs(BENCH_DIR, exist_ok=True)

def record(entry):
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
