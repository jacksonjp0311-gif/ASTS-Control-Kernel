import os
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATE_DIR = os.path.join(ROOT_DIR, "state")

PFP_STATE_FILE = os.path.join(STATE_DIR, "pfp_state.json")

def load_state():
    if not os.path.exists(PFP_STATE_FILE):
        return {
            "last_pulse_step": -10000,
            "pulse_count": 0
        }
    try:
        with open(PFP_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "last_pulse_step": -10000,
            "pulse_count": 0
        }

def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(PFP_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
