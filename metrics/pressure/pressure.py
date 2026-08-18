"""Pressure: how close the loop is to its load budget.

Uses load keys (usage, latency, load, cpu, memory). Complexity is structure, not load.
Values already in [0, 1] are treated as fractions of capacity.
Values above 1 are normalized by MAX_BUDGET.
Returns None when no load key is present.
"""

from metrics.pressure.budgets import MAX_BUDGET

LOAD_KEYS = frozenset({"usage", "latency", "load", "cpu", "memory"})


def _as_fraction(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if x > 1.0:
        cap = float(MAX_BUDGET) if MAX_BUDGET else 100.0
        if cap <= 0.0:
            return None
        x = x / cap
    return max(0.0, min(1.0, x))


def compute_pressure(metrics):
    if not isinstance(metrics, dict) or not metrics:
        return None
    loads = []
    for key, raw in metrics.items():
        if str(key).lower() not in LOAD_KEYS:
            continue
        frac = _as_fraction(raw)
        if frac is not None:
            loads.append(frac)
    if not loads:
        return None
    return max(loads)
