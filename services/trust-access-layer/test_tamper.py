"""Deliberately tamper with a logged entry and confirm the hash chain
detects it. Run with: python test_tamper.py"""
from hashing import compute_entry_hash, verify_chain

entries = []
prev = "0" * 64
for i in range(3):
    payload = {"case_id": f"c{i}", "action": "eligibility_check"}
    h = compute_entry_hash(payload, prev)
    entries.append({"payload": payload, "entry_hash": h})
    prev = h

print("Chain valid before tampering:", verify_chain(entries))
entries[1]["payload"]["action"] = "TAMPERED"
print("Chain valid after tampering: ", verify_chain(entries))
assert verify_chain(entries) is False, "Tamper detection FAILED"
print("Tamper detection confirmed working.")
