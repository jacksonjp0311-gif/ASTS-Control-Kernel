from stress_runner import run_stress

multipliers = [1.0, 1.5, 2.0, 3.0, 4.0]

results = []

for m in multipliers:
    r = run_stress(drift_mult=m, label=f"sweep_drift_{m}")
    results.append(r)

print("\nDRIFT SWEEP RESULTS")
for r in results:
    print(r)
