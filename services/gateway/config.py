import os
from dotenv import load_dotenv
load_dotenv()

ELIGIBILITY_SERVICE_URL = os.getenv("ELIGIBILITY_SERVICE_URL", "http://localhost:8001")
PRECEDENT_SERVICE_URL = os.getenv("PRECEDENT_SERVICE_URL", "http://localhost:8002")
COMPLIANCE_SERVICE_URL = os.getenv("COMPLIANCE_SERVICE_URL", "http://localhost:8003")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
MONITORING_SERVICE_URL = os.getenv("MONITORING_SERVICE_URL", "http://localhost:8005")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
