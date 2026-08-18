"""Inter-report divergence.

Confidence-weighted spread of observer slices on a shared [0, 1] field.
0 = the reports agree. 1 = maximum disagreement.
Returns None when fewer than two usable reports exist.
"""


def _clamp01(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, x))


def _report_value(report):
    metrics = report.get("metrics") if isinstance(report, dict) else None
    if not isinstance(metrics, dict) or not metrics:
        return None
    vals = []
    for raw in metrics.values():
        v = _clamp01(raw)
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    return sum(vals) / float(len(vals))


def _confidence(report):
    if not isinstance(report, dict):
        return 1.0
    c = _clamp01(report.get("confidence", 1.0))
    return 1.0 if c is None else c


def compute_divergence(reports):
    if not reports:
        return None
    points = []
    for report in reports:
        value = _report_value(report)
        if value is None:
            continue
        points.append((value, _confidence(report)))
    if len(points) < 2:
        return None
    weight = sum(w for _, w in points)
    if weight <= 0.0:
        return None
    mean = sum(v * w for v, w in points) / weight
    mad = sum(abs(v - mean) * w for v, w in points) / weight
    # Two reports at 0 and 1 → MAD 0.5 → 1.0
    return _clamp01(2.0 * mad)
