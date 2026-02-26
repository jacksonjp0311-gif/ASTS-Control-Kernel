def deterministic_order(observers):
    return sorted(observers, key=lambda x: x.__class__.__name__)
