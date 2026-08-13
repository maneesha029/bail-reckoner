import hashlib
import json

def compute_entry_hash(record: dict, previous_hash: str) -> str:
    """
    Computes a SHA-256 hash over the canonical JSON representation of the audit record
    (excluding entry_hash and previous_hash) concatenated with previous_hash.
    """
    # Create a copy and remove hash fields if present
    content_dict = {k: v for k, v in record.items() if k not in ("entry_hash", "previous_hash")}
    
    # Sort keys for deterministic output
    canonical_json = json.dumps(content_dict, sort_keys=True, separators=(',', ':'))
    content = canonical_json + previous_hash
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def verify_chain(entries: list[dict]) -> bool:
    """Given entries in chronological order, verify no tampering occurred."""
    prev = "0" * 64
    for entry in entries:
        expected = compute_entry_hash(entry, prev)
        if expected != entry.get("entry_hash"):
            return False
        prev = entry.get("entry_hash")
    return True
