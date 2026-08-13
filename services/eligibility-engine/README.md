# Eligibility Engine

The Eligibility Engine calculates statutory bail eligibility for undertrial
prisoners under Section 436A of the CrPC / Section 479 of the BNSS.

It compares custody time with the applicable threshold:

- Half of the maximum sentence for a normal offender.
- One-third of the maximum sentence for a first-time offender.

The calculation is deterministic and does not use AI.

## Service details

- Service URL: `http://localhost:8001`
- Internal Compose service: `eligibility-engine`
- Database: PostgreSQL through `DATABASE_URL`
- Audit service: `TRUST_SERVICE_URL`

## Database design

This service owns the `cases` and `offenses` tables.

The tables are connected through the `case_offenses` join table:

```text
cases.case_id
    |
    | case_offenses.case_id
    |
case_offenses.(offense_act, offense_section)
    |
    | offenses.(act, section)
    |
offenses
```

The `(act, section)` pair identifies an offense. The eligibility calculation
gets `max_sentence_months` from the linked `offenses` records. For multiple
linked offenses, the charge with the longest maximum sentence supplies the
binding threshold.

The legacy `cases.charges` JSON column is retained for compatibility. New
case links should be inserted into `case_offenses` directly.

## Running with Docker Compose

From the repository root:

```powershell
docker compose up -d --build
```

Check service status:

```powershell
docker compose ps
```

Seed the offense database:

```powershell
docker compose exec eligibility-engine python seed_offenses.py
```

## Creating and linking a case

Insert a case using an offense that exists in `offenses`. For example,
`IPC 379`:

```powershell
docker compose exec postgres psql -U user -d bail_reckoner -c 'INSERT INTO cases (case_id, prisoner_id, custody_start_date, is_first_time_offender, state, district, case_stage, has_legal_aid, charges, created_at, updated_at) VALUES (''case-example'', ''prisoner-example'', ''2024-01-01'', false, ''Delhi'', ''New Delhi'', ''under_trial'', true, $$[{"act":"IPC","section":"379","offense_category":"general","is_compoundable":true,"max_sentence_months":36}]$$, NOW(), NOW()) ON CONFLICT (case_id) DO NOTHING;'
```

For legacy cases whose offense information is only in `cases.charges`, run:

```powershell
docker compose exec eligibility-engine python link_case_offenses.py
```

For new cases, the relationship can be created directly:

```powershell
docker compose exec postgres psql -U user -d bail_reckoner -c "INSERT INTO case_offenses (case_id, offense_act, offense_section) VALUES ('case-example', 'IPC', '379');"
```

Verify the relationship:

```powershell
docker compose exec postgres psql -U user -d bail_reckoner -c "SELECT c.case_id, co.offense_act, co.offense_section, o.offense_category, o.max_sentence_months FROM cases c JOIN case_offenses co ON co.case_id = c.case_id JOIN offenses o ON o.act = co.offense_act AND o.section = co.offense_section WHERE c.case_id = 'case-example';"
```

## API endpoints

### Check eligibility

```text
POST /api/v1/eligibility/check
```

Request:

```json
{"case_id":"case-example"}
```

The endpoint reads the case and its linked offenses, calculates the result,
caches the last computed result in the running service, and sends an audit
request to Member 4's trust-access-layer.

### Get the last computed result

```text
GET /api/v1/eligibility/{case_id}
```

This returns the last computed result without recalculating eligibility.

### Review or override

```text
POST /api/v1/eligibility/override
```

Required header:

```text
X-Actor-Role: judge
```

The role must be `judge` or `legal_aid`.

Request:

```json
{
  "case_id":"case-example",
  "actor_user_id":"user-example",
  "reason":"Reviewed custody calculation"
}
```

An override is stored beside the computed result and does not replace it.

All endpoints use the standard response envelope:

```json
{"success":true,"data":{},"error":null}
```

## Example test

For a non-first-time offender charged under `IPC 379`:

```text
Maximum sentence: 36 months
Calculated term: 36 × 30 = 1080 days
Required half-term: 540 days
```

For a first-time offender charged under `PMLA Section 4`:

```text
Maximum sentence: 84 months
Calculated term: 84 × 30 = 2520 days
Required one-third term: 840 days
```

Run the API check with:

```powershell
curl.exe -X POST http://localhost:8001/api/v1/eligibility/check `
  -H "Content-Type: application/json" `
  -d '{"case_id":"case-example"}'
```

## Testing

Compile the service:

```powershell
python -m compileall services/eligibility-engine
```

Run the tests from the service directory after installing requirements:

```powershell
cd services/eligibility-engine
python -m pytest test_main.py -v
```

The tests cover offense categories, insufficient data, the first-time
offender rule, and multiple charges.

## Audit logging boundary

The eligibility engine does not own the `audit_logs` table. For every check
and override, it calls:

```text
{TRUST_SERVICE_URL}/api/v1/audit/log
```

The trust-access-layer, owned by Member 4, is responsible for creating and
persisting audit records.

## Important notes

- A case without a linked offense returns `insufficient_data`.
- The offense `(act, section)` must exist before it can be linked.
- `link_case_offenses.py` is a migration/backfill script, not a requirement
  for cases that insert directly into `case_offenses`.
- Results and overrides are currently held in the running eligibility
  service's memory; they are lost if that container restarts.
