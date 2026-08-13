# Trust & Access Layer

The Trust & Access Layer service for Bail Reckoner. Provides JWT-based authentication, RBAC, and tamper-evident audit logging for the system.

## Architecture

This service uses FastAPI and SQLAlchemy to interact with a PostgreSQL database. It owns the `users` and `audit_logs` tables. 

### Concurrency Protection & Append-Only Audit Logs

- **Concurrency:** Audit log insertions are serialized using PostgreSQL Advisory Locks (`pg_advisory_xact_lock`) on a specific key. This prevents race conditions where concurrent inserts might read the same `previous_hash` and cause the chain to fork.
- **Append-Only Protection:** A PostgreSQL trigger (`audit_log_append_only`) automatically blocks any `UPDATE` or `DELETE` operations on the `audit_logs` table, ensuring immutability at the database level.
- **Encryption at Rest:** Ensure PostgreSQL cluster-level or disk-level encryption is enabled in production. Personally Identifiable Information (PII) is minimized in the audit payloads. Passwords are never logged or exposed and are hashed using bcrypt password hashing.

## Setup

1. Configure `.env` (or use the defaults in `config.py`):
   - `DATABASE_URL` (e.g., `postgresql://postgres:postgres@localhost:5432/bail_reckoner`)
   - `JWT_SECRET` (Must be a secure random string)
   - `RATE_LIMIT` (e.g., `5/minute`)
   - `HTTPS_ENFORCED` (set to `true` for production)
2. Run database migrations / init:
   The database will auto-initialize on first startup, or you can run the seed script:
   ```bash
   python seed_users.py
   ```
3. Run the service:
   ```bash
   uvicorn main:app --reload
   ```

## Integration Instructions

### For Members 1, 2, 3, and 5 (Audit Log Insertion)

When making internal calls to insert an audit log, you must provide a valid internal or admin JWT in the `Authorization` header.

**Endpoint:** `POST /api/v1/audit/log`

**Request Headers:**
```http
Authorization: Bearer <your_internal_jwt>
```

**Request Body Example:**
```json
{
  "case_id": "c-1234",
  "actor_user_id": "uuid-here",
  "actor_role": "judge",
  "action_type": "eligibility_check",
  "action_payload": { "reason": "example" }
}
```

### For Member 6 (Gateway & Auth)

The gateway will validate JWTs issued by this service. Ensure both services share the exact same `JWT_SECRET` via environment variables.

The token payload contains:
```json
{
  "user_id": "uuid-string",
  "role": "judge|legal_aid|jail_officer|admin",
  "exp": 1723555200
}
```
Tokens are generated using `HS256`. Expired tokens will fail validation.

## Demonstrating Tamper Detection

To verify the hash chain and the append-only protection, run:
```bash
python test_tamper.py
```
This script will initialize the DB, insert valid records, attempt (and be blocked from) a normal `UPDATE`, then bypass the trigger to show that tampering is detected by the hash chain validation.
