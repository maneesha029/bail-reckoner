import os
from dotenv import load_dotenv
load_dotenv()

CHROMA_URL = os.getenv("CHROMA_URL", "http://localhost:8010")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TRUST_SERVICE_URL = os.getenv("TRUST_SERVICE_URL", "http://localhost:8004")
