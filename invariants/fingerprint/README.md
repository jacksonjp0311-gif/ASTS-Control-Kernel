# Fingerprint Invariants
This directory implements payload fingerprinting utilities.

## What it does
- Computes stable SHA-256 fingerprints for telemetry payloads.
- Hosts lightweight validator/registry scaffolding.

## Mini directory
- `fingerprint.py`
- `validators.py`
- `registry.py`

## Notes
- Fingerprints should use canonicalized serialization (`sort_keys=True`).
