import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/bail_reckoner")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
# Used by routes.py to confirm a case exists in Member 1's `cases`
# table before returning procedural requirements. Read-only against
# `cases`/`offenses` - this service only ever writes to
# procedural_requirements and bond_waiver_flags.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
