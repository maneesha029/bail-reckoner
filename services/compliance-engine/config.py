import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/bail_reckoner")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
