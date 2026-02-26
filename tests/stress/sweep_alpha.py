from stress_runner import run_stress

alphas = [0.5, 0.7, 0.85, 0.92, 0.97]

results = []

for a in alphas:
    r = run_stress(alpha=a, label=f"sweep_alpha_{a}")
    results.append(r)

print("\nALPHA SWEEP RESULTS")
for r in results:
    print(r)
