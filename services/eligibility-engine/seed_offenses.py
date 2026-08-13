"""Load verified offense data into the offenses table.

Usage, from this directory:

    python seed_offenses.py

The script expects offense_data.json beside this file. Each item must contain
only the fields owned by the Offense model:
act, section, offense_category, is_compoundable, max_sentence_months.
"""

import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import DATABASE_URL
from models import Base, Offense


DATA_FILE = Path(__file__).with_name("offense_data.json")
OFFENSE_CATEGORIES = {
    "cyber_crimes",
    "crimes_against_sc_st",
    "crimes_against_women",
    "crimes_against_children",
    "offences_against_state",
    "economic_offences",
    "crimes_against_foreigners",
    "general",
}
ACTS = {"IPC", "BNS", "BNSS", "BSA", "IT_Act", "POCSO", "SC_ST_Act", "PMLA", "Foreigners_Act", "other"}
REQUIRED_FIELDS = {
    "act",
    "section",
    "offense_category",
    "is_compoundable",
    "max_sentence_months",
}


def load_offense_data() -> list[dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}. Add verified offense rows first.")

    with DATA_FILE.open(encoding="utf-8") as file:
        rows = json.load(file)

    if not isinstance(rows, list):
        raise ValueError("offense_data.json must contain a JSON array")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Row {index} must be a JSON object")
        if set(row) != REQUIRED_FIELDS:
            raise ValueError(
                f"Row {index} must contain exactly {sorted(REQUIRED_FIELDS)}"
            )
        if row["act"] not in ACTS:
            raise ValueError(f"Row {index} has an invalid act: {row['act']}")
        if row["offense_category"] not in OFFENSE_CATEGORIES:
            raise ValueError(
                f"Row {index} has an invalid offense_category: "
                f"{row['offense_category']}"
            )
        if not isinstance(row["section"], str) or not row["section"].strip():
            raise ValueError(f"Row {index} must have a non-empty section")
        if not isinstance(row["is_compoundable"], bool):
            raise ValueError(f"Row {index} is_compoundable must be boolean")
        if not isinstance(row["max_sentence_months"], int) or row["max_sentence_months"] < 0:
            raise ValueError(f"Row {index} max_sentence_months must be a non-negative integer")

    return rows


def seed_offenses() -> int:
    rows = load_offense_data()
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for row in rows:
            session.merge(Offense(**row))
        session.commit()

    return len(rows)


if __name__ == "__main__":
    count = seed_offenses()
    print(f"Seeded {count} offense(s) into offenses")
