import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/bail_reckoner")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ELIGIBILITY_SERVICE_URL = os.getenv("ELIGIBILITY_SERVICE_URL", "http://localhost:8001")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
SMTP_HOST = os.getenv("SMTP_HOST", "")
