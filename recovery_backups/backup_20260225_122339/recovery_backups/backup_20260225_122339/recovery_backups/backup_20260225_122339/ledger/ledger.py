import json, os

LEDGER_FILE = "ledger.json"

def append_entry(entry):
    if not os.path.exists(LEDGER_FILE):
        data = []
    else:
        with open(LEDGER_FILE, "r") as f:
            data = json.load(f)

    data.append(entry)

    with open(LEDGER_FILE, "w") as f:
        json.dump(data, f, indent=2)
