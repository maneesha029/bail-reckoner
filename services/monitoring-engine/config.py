"""
Configuration management for Monitoring & Outreach Engine.

Loads environment variables from .env file.
All sensitive values (API URLs, credentials) come from environment, not code.

Time Complexity: O(1) — environment variable lookup is constant time
Space Complexity: O(1) — fixed set of config variables
"""

import os
from functools import lru_cache
from dotenv import load_dotenv


# Load .env file (for development)
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/bail_reckoner"
    )
    
    # Redis (for Celery scheduling)
    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    
    # External service URLs
    ELIGIBILITY_SERVICE_URL = os.getenv(
        "ELIGIBILITY_SERVICE_URL",
        "http://localhost:8001"  # Member 1
    )
    
    TRUST_SERVICE_URL = os.getenv(
        "TRUST_SERVICE_URL",
        "http://localhost:8004"  # Member 4
    )
    
    # SMTP Configuration (email notifications)
    SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@bailreckoner.in")
    
    # Twilio Configuration (SMS notifications - stretch goal)
    TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
    
    # Scheduler Configuration
    SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "30"))
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
    
    # Application
    APP_NAME = "Monitoring & Outreach Engine"
    APP_VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""
    SMTP_ENABLED = True
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "tanmay.bpatil07@gmail.com"
    SMTP_PASSWORD = "your-16-character-app-password"
    SMTP_FROM_EMAIL = "your-email@gmail.com"
    SMTP_TLS = True
    DEBUG = True
    SCHEDULER_ENABLED = False  # Disable scheduler in dev by default


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SCHEDULER_ENABLED = True


class TestingConfig(Config):
    """Testing configuration."""
    DATABASE_URL = "sqlite:///:memory:"
    REDIS_URL = "redis://localhost:6379/1"  # Different DB for tests
    DEBUG = True
    SCHEDULER_ENABLED = False


@lru_cache()
def get_config():
    """
    Get configuration based on environment.
    
    Returns the appropriate Config class based on ENV variable.
    Cached for performance.
    
    Time Complexity: O(1) — simple string comparison + lookup
    Space Complexity: O(1) — returns singleton cached object
    """
    env = os.getenv("ENV", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Export config instance for import in other modules
config = get_config()