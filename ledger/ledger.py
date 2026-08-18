"""Append-only JSONL ledger. One hashed record per line. Never rewritten."""

from __future__ import annotations

import json
import os
from typing import Any

from ledger.hashchain import GENESIS, digest, verify_records

LEDGER_FILE = "ledger.jsonl"


def _path(path: str | None = None) -> str:
    return path or LEDGER_FILE


def _read_records(path: str) -> list[dict[str, Any]]:
    if not os.path.exists(path):
        return []
    out: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if isinstance(rec, dict):
                out.append(rec)
    return out


def append_entry(entry: Any, path: str | None = None) -> dict[str, Any]:
    ledger_path = _path(path)
    records = _read_records(ledger_path)
    prev = records[-1]["hash"] if records else GENESIS
    seq = (int(records[-1]["seq"]) + 1) if records else 1
    rec = {
        "seq": seq,
        "prev": prev,
        "hash": digest(prev, entry),
        "entry": entry,
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str) + "\n")
    return rec


def replay(path: str | None = None) -> list[Any]:
    records = _read_records(_path(path))
    errors = verify_records(records)
    if errors:
        raise ValueError("ledger chain broken: " + "; ".join(errors[:4]))
    return [rec.get("entry") for rec in records]


def verify(path: str | None = None) -> list[str]:
    return verify_records(_read_records(_path(path)))
