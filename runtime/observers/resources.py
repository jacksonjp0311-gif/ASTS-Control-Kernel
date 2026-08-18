"""Resource slice from the live ASTS host process."""

from adapters.host_process.probe import sample, usage_fraction
from runtime.observers.plant import is_simulated, observe_resources_plant


def observe_resources(env):
    if is_simulated(env):
        return observe_resources_plant(env)
    host = env.get("host") if isinstance(env, dict) else None
    if not isinstance(host, dict):
        host = sample()
    usage = usage_fraction(host.get("rss_bytes"))
    metrics = {}
    if usage is not None:
        metrics["usage"] = usage
    return {
        "domain": "resources",
        "metrics": metrics,
        "confidence": 0.95 if usage is not None else 0.0,
        "source": "host_process",
    }
