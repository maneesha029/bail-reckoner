"""
Seeds real CaseRecord rows into Postgres, linked to real Offense rows
via the case_offenses table, so check_eligibility() has something to
find. Before this script existed, no code path anywhere ever inserted
a CaseRecord - every case_id 404'd.

Run order matters:
    1. python seed_offenses.py     <- loads the offenses reference table
    2. python seed_cases.py        <- this script, needs #1 done first

Safe to re-run: it skips any case_id that already exists rather than
duplicating or erroring.

case_id values below (case-001 ... case-010) intentionally match the
demo roster used in the frontend's mock roster data, so clicking a
person in the Roster tab opens a case that actually resolves.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from config import DATABASE_URL
from models import Base, CaseRecord, Offense

# (case_id, prisoner display name, days already in custody,
#  is_first_time_offender, state, district, case_stage, has_legal_aid,
#  [(act, section), ...])   <- must exactly match offense_data.json entries
CASES = [
    # NOTE: monitoring-engine's /alerts/scan is hardcoded to only check
    # case-001 and case-002 (see routes.py trigger_scan). case-001's days
    # are deliberately set past its threshold (IPC 379, not first-time =
    # 540 days required) so "Run scan now" in the Calendar tab has a real
    # alert to produce during a demo, instead of silently finding nothing.
    ("case-001", "Ramesh Kumar Yadav", 600, False, "Uttar Pradesh", "Lucknow",
     "under_trial", True, [("IPC", "379")]),
    ("case-002", "Suresh Prajapati", 200, True, "Uttar Pradesh", "Kanpur",
     "under_trial", True, [("IPC", "379")]),
    ("case-003", "Priya Sharma", 90, False, "Delhi", "South Delhi",
     "under_trial", True, [("IPC", "354")]),
    ("case-004", "Anita Devi", 150, True, "Bihar", "Patna",
     "under_trial", True, [("BNS", "74")]),
    ("case-005", "Mohammed Aslam", 500, False, "Maharashtra", "Mumbai",
     "under_trial", True, [("IT_Act", "66")]),
    ("case-006", "Vikram Singh Rathore", 600, False, "Rajasthan", "Jaipur",
     "under_trial", False, [("PMLA", "4")]),
    ("case-007", "Farhan Ahmed Khan", 700, False, "West Bengal", "Kolkata",
     "under_trial", True, [("SC_ST_Act", "3(1)(r)")]),
    ("case-008", "Sunita Kumari", 60, True, "Bihar", "Gaya",
     "under_trial", True, [("IPC", "379"), ("BNS", "74")]),
    ("case-009", "Om Prakash Chaudhary", 450, False, "Haryana", "Gurugram",
     "bail_applied", True, [("IPC", "379")]),
    ("case-010", "Geeta Bai Solanki", 420, True, "Gujarat", "Ahmedabad",
     "under_trial", True, [("POCSO", "12")]),
]


def run():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)

    created = 0
    skipped = 0

    with Session(engine) as session:
        for (case_id, prisoner_name, days_in_custody, is_first_time, state,
             district, case_stage, has_legal_aid, offense_refs) in CASES:

            existing = session.scalar(select(CaseRecord).where(CaseRecord.case_id == case_id))
            if existing:
                skipped += 1
                continue

            offenses = []
            for act, section in offense_refs:
                offense = session.scalar(
                    select(Offense).where(Offense.act == act, Offense.section == section)
                )
                if offense is None:
                    raise RuntimeError(
                        f"{case_id}: offense {act} {section} not found - "
                        f"did you run `python seed_offenses.py` first?"
                    )
                offenses.append(offense)

            custody_start = datetime.now(timezone.utc) - timedelta(days=days_in_custody)
            now = datetime.now(timezone.utc)

            case = CaseRecord(
                case_id=case_id,
                # NOTE: this model has no dedicated name/photo field yet.
                # Using prisoner_id to carry a readable display name is a
                # stopgap for demo purposes - the real fix is adding a
                # `prisoner_name` (and later `photo_url`) column here.
                prisoner_id=prisoner_name,
                custody_start_date=custody_start,
                is_first_time_offender=is_first_time,
                state=state,
                district=district,
                case_stage=case_stage,
                has_legal_aid=has_legal_aid,
                charges=[
                    {"act": o.act, "section": o.section,
                     "offense_category": o.offense_category,
                     "is_compoundable": o.is_compoundable,
                     "max_sentence_months": o.max_sentence_months}
                    for o in offenses
                ],
                created_at=now,
                updated_at=now,
            )
            case.offense_records = offenses  # populates case_offenses directly
            session.add(case)
            created += 1

        session.commit()

    print(f"Seeded {created} cases ({skipped} already existed, skipped).")
    print("Case IDs you can now test with:")
    for c in CASES:
        print(f"  {c[0]}  -  {c[1]}")


if __name__ == "__main__":
    run()