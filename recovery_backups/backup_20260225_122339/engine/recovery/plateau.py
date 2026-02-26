import json, os

STATE = os.path.join(os.path.dirname(__file__), "..","..","state","plateau_state.json")

def load():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"count":0}

def save(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE,"w"))

def check(drift_slow, threshold=0.015, steps=3):
    s = load()
    if drift_slow >= threshold:
        s["count"] += 1
    else:
        s["count"] = 0
    save(s)
    return s["count"] >= steps
