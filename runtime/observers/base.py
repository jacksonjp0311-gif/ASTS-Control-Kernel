from runtime.observers.code_structure import observe_code
from runtime.observers.runtime_exec import observe_runtime
from runtime.observers.reasoning_quality import observe_reasoning
from runtime.observers.resources import observe_resources
from runtime.observers.integration import observe_integration

def run_observers(env):
    return [
        observe_code(env),
        observe_runtime(env),
        observe_reasoning(env),
        observe_resources(env),
        observe_integration(env)
    ]
