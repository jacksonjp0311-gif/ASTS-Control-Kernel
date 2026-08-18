# Ledger

Append-only JSONL history. One hashed record per line. The file is never rewritten.

## What it does
- `append_entry` writes one `ledger.jsonl` line: `{seq, prev, hash, entry}`
- `hashchain` SHA-256 links each record to the previous hash
- `replay` returns entries only if the chain verifies
- `compact` refuses — this log is not compacted

## Mini directory
- `ledger.py`
- `hashchain.py`
- `replay.py`
- `compaction.py`

## Notes
- Genesis prev is 64 zeros.
- Runtime artifact: `ledger.jsonl` in the process cwd (gitignored).
