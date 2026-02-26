def observe_runtime(env):
    step = env.get('step', 0)
    latency = 0.3 + (0.02 * step)
    latency = max(0, min(1, latency))
    return {
        'domain': 'runtime',
        'metrics': {'latency': latency},
        'confidence': 0.8
    }
