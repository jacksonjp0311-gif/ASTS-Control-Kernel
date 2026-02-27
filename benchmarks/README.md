# Benchmarks

Tools for running and analyzing ASTS stability experiments.

## Files
- `run_pfp_benchmark.py`: executes step loop and writes JSONL run artifacts.
- `pfp_report.py`: computes summary stats from latest run.
- `pfp_export_csv.py`: exports benchmark runs as CSV.
- `run_all.py`: convenience orchestration wrapper.
- `recorder.py`: append-only event recorder utility.

## Output
Generated outputs are written under:
- `benchmarks/runs/`
- `benchmarks/reports/`
