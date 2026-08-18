"""Runtime slice from the previous step's real wall time."""

from adapters.host_process.probe import latency_fraction
from runtime.observers.plant import is_simulated, observe_runtime_plant


def observe_runtime(env):
    if is_simulated(env):
        return observe_runtime_plant(env)
    step_dt = env.get("step_dt") if isinstance(env, dict) else None
    latency = latency_fraction(step_dt)
    metrics = {}
    if latency is not None:
        metrics["latency"] = latency
    return {
        "domain": "runtime",
        "metrics": metrics,
        "confidence": 0.95 if latency is not None else 0.0,
        "source": "host_process",
    }
