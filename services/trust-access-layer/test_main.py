from hashing import compute_entry_hash, verify_chain
from auth import role_can


def test_hash_chain_detects_tamper():
    prev = "0" * 64
    h1 = compute_entry_hash({"a": 1}, prev)
    entries = [{"payload": {"a": 1}, "entry_hash": h1}]
    assert verify_chain(entries) is True
    entries[0]["payload"]["a"] = 2
    assert verify_chain(entries) is False


def test_role_permissions():
    assert role_can("judge", "override") is True
    assert role_can("jail_officer", "override") is False
