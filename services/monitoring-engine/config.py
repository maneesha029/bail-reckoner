import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/bail_reckoner")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ELIGIBILITY_SERVICE_URL = os.getenv("ELIGIBILITY_SERVICE_URL", "http://localhost:8001")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", SMTP_HOST)
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"