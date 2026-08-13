import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@postgres:5432/bail_reckoner")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
TRUST_SERVICE_TOKEN = os.getenv('TRUST_SERVICE_TOKEN', '')



