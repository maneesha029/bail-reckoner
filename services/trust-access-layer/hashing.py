import hashlib
import json


def compute_entry_hash(payload: dict, previous_hash: str) -> str:
    content = json.dumps(payload, sort_keys=True) + previous_hash
    return hashlib.sha256(content.encode()).hexdigest()


def verify_chain(entries: list[dict]) -> bool:
    """Given entries in chronological order, verify no tampering occurred."""
    prev = "0" * 64
    for entry in entries:
        expected = compute_entry_hash(entry["payload"], prev)
        if expected != entry["entry_hash"]:
            return False
        prev = entry["entry_hash"]
    return True
