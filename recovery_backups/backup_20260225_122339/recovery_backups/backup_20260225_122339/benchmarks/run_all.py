import os
import sys

# --- PROJECT ROOT BOOTSTRAP (additive) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------------------------------
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)

def main():
    # 1) run benchmark
    run([sys.executable, os.path.join("benchmarks", "run_pfp_benchmark.py")])

    # 2) report latest
    run([sys.executable, os.path.join("benchmarks", "pfp_report.py")])

    # 3) export csv
    run([sys.executable, os.path.join("benchmarks", "pfp_export_csv.py")])

if __name__ == "__main__":
    main()
