from typing import Dict, Any
from metrics.drift.drift import reset_baseline

def execute(decision: Dict[str, Any], theta: Dict[str, Any], root_dir: str) -> Dict[str, Any]:
    """
    Safe execution of recovery actions.
    This is the only place side-effects should happen.
    """
    actions = decision.get("actions", []) or []
    out = dict(decision)

    if "reset_baseline" in actions:
        try:
            reset_baseline(theta.get("metrics", {}))
            out["did_reset_baseline"] = True
        except Exception:
            out["did_reset_baseline"] = False

    # 'tighten_constraints' and 'request_validation' are advisory for now.
    # If you later wire them into control/governor/pfp, do it here.

    return out
