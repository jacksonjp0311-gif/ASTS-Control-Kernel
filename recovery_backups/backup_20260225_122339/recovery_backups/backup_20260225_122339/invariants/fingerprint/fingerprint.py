import hashlib, json
def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
