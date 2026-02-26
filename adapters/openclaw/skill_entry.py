import sys
from pathlib import Path

# ensure repo root is importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from engine.execution.runner import run_step
except Exception as e:
    raise RuntimeError(f"Engine import failed: {e}")

def run_skill(env):
    result = run_step(env)

    if isinstance(result, tuple):
        theta = result[0]
        monitor_bundle = result[1] if len(result) > 1 else {}
    else:
        theta = result
        monitor_bundle = {}

    return {
        "theta": theta,
        "pfp": monitor_bundle if isinstance(monitor_bundle, dict) else {}
    }
