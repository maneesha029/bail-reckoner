# FINAL INTEGRATION CHECK
### Run This After All 6 Members Have Completed Their Parts

---

## STEP 1: BRING EVERYTHING UP TOGETHER

```bash
docker-compose up --build
```

- [ ] All 10 containers (postgres, redis, chroma, 5 backend services, gateway, frontend) start without errors
- [ ] No port conflicts, no missing environment variables (check every service's logs for startup errors)
- [ ] The frontend loads at its local URL and doesn't show connection errors on first load

---

## STEP 2: SERVICE-BY-SERVICE HEALTH CHECK

Call each service directly (bypass the gateway first, to isolate problems):
- [ ] `POST /api/v1/eligibility/check` (Member 1) returns a valid response for a real case_id
- [ ] `POST /api/v1/precedent/search` (Member 2) returns a valid response
- [ ] `POST /api/v1/procedural/requirements` and `POST /api/v1/bond-waiver/check` (Member 3) both return valid responses
- [ ] `POST /api/v1/auth/login` (Member 4) returns a valid JWT for each of the 4 roles
- [ ] `GET /api/v1/alerts/pending` (Member 5) returns a valid response

If any of these fail in isolation, fix it before testing through the gateway — isolating the problem here saves hours of confused gateway-level debugging.

---

## STEP 3: GATEWAY ROUTING CHECK

- [ ] Every route in Member 6's routing table correctly forwards to the right service (test each prefix once)
- [ ] Auth middleware correctly rejects requests without a valid JWT
- [ ] Auth middleware correctly rejects a role trying to access an endpoint it shouldn't (e.g., jail_officer hitting a judge-only route, if any exist)

---

## STEP 4: THE HONEST TEST (This Is the Real Bar — Not Optional)

1. **Create a brand new case** through the system — never-before-seen offense combination and custody date
2. Confirm **every dashboard section reflects this specific case correctly**: eligibility numbers match the actual custody math, precedent citations are relevant to the actual offense category, procedural checklist matches the actual offense, bond-waiver flag responds to actual hardship inputs
3. **Create a second, different case** and confirm every section changes again, correctly, differently from the first
4. Check the audit log for both cases — confirm real entries exist with correct, unbroken hash-chaining
5. Log in as each of the 4 roles and confirm dashboard access restrictions hold correctly
6. Trigger a manual override on one case and confirm it's logged, and the original computed result is preserved alongside it, not overwritten
7. Run the tamper-test script (Member 4's `test_tamper.py`) live and confirm detection works

**If any single item above fails, that feature is not done — send it back to the owning member with the specific failure. Do not patch around it as a shortcut.**

---

## STEP 5: CROSS-CUTTING CHECKS

- [ ] **Graceful degradation:** manually stop one backend service (e.g., `docker-compose stop precedent-engine`) and confirm the dashboard still loads, showing the other sections correctly with a clear "temporarily unavailable" message for the stopped service — not a broken page
- [ ] **Load check:** insert Member 5's larger synthetic dataset (or generate a few thousand records) and confirm the scanner and dashboard queue still perform reasonably
- [ ] **Data labeling:** confirm any synthetic data is clearly marked as such wherever it appears in the UI or exported reports — never presented as real without qualification

---

## STEP 6: DEPLOYMENT VERIFICATION

- [ ] The full system is deployed and reachable at a public URL
- [ ] Repeat the Honest Test (Step 4) on the **live deployed link**, not localhost
- [ ] Test the live link from a device none of you have used for development — a phone, a different laptop — to catch anything that only worked because of a cached local setting
- [ ] Confirm HTTPS is active and the login/auth flow works correctly in production

---

## STEP 7: SIGN-OFF

Only mark the project complete when every checkbox above is checked, on the live deployed system, confirmed by more than one team member independently (not just the person who built that piece).
