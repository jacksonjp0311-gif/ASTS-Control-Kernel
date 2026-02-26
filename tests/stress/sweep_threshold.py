from stress_runner import run_stress

thresholds = [1.0, 1.5, 2.0, 3.0]

results = []

for t in thresholds:
    r = run_stress(threshold_mult=t, label=f"sweep_threshold_{t}")
    results.append(r)

print("\nTHRESHOLD SWEEP RESULTS")
for r in results:
    print(r)
