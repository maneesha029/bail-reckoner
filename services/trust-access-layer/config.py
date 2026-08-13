import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/bail_reckoner")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/minute")
HTTPS_ENFORCED = os.getenv("HTTPS_ENFORCED", "false").lower() == "true"
