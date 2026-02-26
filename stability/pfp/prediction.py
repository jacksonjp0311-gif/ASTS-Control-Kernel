def predict_drift(current_slow, previous_slow):
    if previous_slow is None:
        return current_slow
    slope = current_slow - previous_slow
    return current_slow + slope
