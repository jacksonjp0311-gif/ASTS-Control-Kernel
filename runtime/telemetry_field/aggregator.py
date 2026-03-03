from metrics.drift.drift import compute_drift
from metrics.drift.multiscale import multi_scale
from metrics.divergence.divergence import compute_divergence
from metrics.pressure.pressure import compute_pressure
from invariants.fingerprint.fingerprint import fingerprint

def aggregate(reports):
    # Merge metrics from observers (last write wins; deterministic by observer order)
    metrics = {}
    for r in reports:
        metrics.update(r.get('metrics', {}))

    D_total, per_key = compute_drift(metrics)
    D_ms = multi_scale(D_total)  # persisted state: fast/slow

    V = compute_divergence(reports)
    P = compute_pressure(metrics)

    # Fingerprint over the observable payload (metrics only for now; expand later)
    H = fingerprint(metrics)

    return {
        'metrics': metrics,
        'drift': {
            'total': D_total,
            'fast': D_ms.get('fast', 0.0),
            'slow': D_ms.get('slow', 0.0),
            'per_key': per_key
        },
        'divergence': V,
        'pressure': P,
        'hash': H
    }
