import json
import os
from typing import Dict, Tuple

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "state")
BASELINE_FILE = os.path.join(STATE_DIR, "baseline_metrics.json")

def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))

def _load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def _sanitize_metrics(m: Dict) -> Dict[str, float]:
    out = {}
    if not isinstance(m, dict):
        return out
    for k, v in m.items():
        out[str(k)] = _clamp01(v)
    return out

def ensure_baseline(metrics: Dict) -> Dict[str, float]:
    """"Create baseline if missing; return baseline dict."""""
    metrics = _sanitize_metrics(metrics)
    baseline = _load_json(BASELINE_FILE)
    if baseline is None:
        _save_json(BASELINE_FILE, metrics)
        return metrics
    return _sanitize_metrics(baseline)

def compute_drift(metrics: Dict) -> Tuple[float, Dict[str, float]]:
    """"Return (D_k in [0,1], per_key_abs_delta dict)."""""
    current = _sanitize_metrics(metrics)
    baseline = ensure_baseline(current)

    keys = set(current.keys()) | set(baseline.keys())
    if not keys:
        return 0.0, {}

    deltas = {}
    total = 0.0
    for k in sorted(keys):
        a = current.get(k, 0.0)
        b = baseline.get(k, 0.0)
        d = abs(a - b)
        d = _clamp01(d)
        deltas[k] = d
        total += d

    D = total / float(len(keys))
    return _clamp01(D), deltas

def reset_baseline(metrics: Dict) -> None:
    """"Manually reset baseline to current metrics."""""
    _save_json(BASELINE_FILE, _sanitize_metrics(metrics))
