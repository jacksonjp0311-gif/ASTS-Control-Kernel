# Ledger
This directory contains append-log helpers and future ledger hardening stubs.

## What it does
- Records step events as immutable history (`ledger.json`).

## How it works
- `ledger.py` appends events.
- `replay.py`, `compaction.py`, and `hashchain.py` provide extension points.

## Mini directory
- `ledger.py`
- `replay.py`
- `compaction.py`
- `hashchain.py`

## Notes
- Preserve append-only semantics for forensic integrity.
