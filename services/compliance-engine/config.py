import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/bail_reckoner")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
# Used by routes.py to resolve offense_category from case_id, joining
# Member 1's case_offenses/offenses tables. Read-only against those
# tables - this service only ever writes to procedural_requirements and
# bond_waiver_flags.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
