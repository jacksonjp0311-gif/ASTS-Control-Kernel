"""Hash-chain helpers for the append-only ledger."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

GENESIS = "0" * 64


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def digest(prev_hash: str, entry: Any) -> str:
    payload = f"{prev_hash}:{canonical(entry)}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_records(records: Iterable[Mapping[str, Any]]) -> list[str]:
    """Return a list of error strings. Empty means the chain holds."""
    errors: list[str] = []
    expected_prev = GENESIS
    expected_seq = 1
    for i, rec in enumerate(records):
        if not isinstance(rec, Mapping):
            errors.append(f"record {i}: not an object")
            continue
        seq = rec.get("seq")
        prev = rec.get("prev")
        got = rec.get("hash")
        entry = rec.get("entry")
        if seq != expected_seq:
            errors.append(f"record {i}: seq {seq} != {expected_seq}")
        if prev != expected_prev:
            errors.append(f"record {i}: prev link broken")
        expect = digest(str(prev or ""), entry)
        if got != expect:
            errors.append(f"record {i}: hash mismatch")
        expected_prev = str(got or "")
        expected_seq += 1
    return errors
