"""Backfill relational case/offense links from legacy cases.charges JSON.

Run after cases and offenses have been seeded:

    python link_case_offenses.py

New case writers should insert rows in case_offenses directly and should not
depend on the legacy JSON charges column.
"""

import json

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from config import DATABASE_URL
from models import Base, CaseRecord, Offense


def link_case_offenses() -> int:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    linked = 0

    with Session(engine) as session:
        cases = session.scalars(select(CaseRecord)).all()
        for case in cases:
            for charge in case.charges or []:
                act = charge.get("act")
                section = charge.get("section")
                if not act or not section:
                    raise ValueError(f"Case {case.case_id} has a charge without act/section")

                offense = session.get(Offense, (act, section))
                if offense is None:
                    raise ValueError(
                        f"No offense found for case {case.case_id}: {act} {section}"
                    )
                if offense not in case.offense_records:
                    case.offense_records.append(offense)
                    linked += 1

        session.commit()

    return linked


if __name__ == "__main__":
    print(f"Linked {link_case_offenses()} case charge(s)")
