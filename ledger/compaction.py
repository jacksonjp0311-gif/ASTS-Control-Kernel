"""The live ledger is append-only. Compaction is refused on purpose."""


def compact():
    return {
        "compacted": False,
        "reason": "append-only ledger is not compacted",
    }
