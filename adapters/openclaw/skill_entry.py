from engine.runner import run_step

def run_skill(env):
    result = run_step(env)

    # tolerant unpack
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
