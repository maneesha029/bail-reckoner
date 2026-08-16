"""
Structured logging configuration for the Monitoring Engine.
Uses JSON format for ELK stack integration.
"""

import logging
import json
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger

# Configure JSON logging
def setup_logging():
    """Setup structured JSON logging."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # JSON formatter
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    # File handler (optional - for local logging)
    try:
        file_handler = logging.FileHandler('monitoring-engine.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")
    
    return logger

# Get logger instance
logger = setup_logging()

# Example usage functions
def log_alert_created(case_id: str, alert_id: str, prisoner_id: str, state: str, district: str):
    """Log alert creation with structured data."""
    logger.info(
        "Alert created",
        extra={
            "case_id": case_id,
            "alert_id": alert_id,
            "prisoner_id": prisoner_id,
            "state": state,
            "district": district,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def log_email_sent(to_email: str, alert_id: str, status: str):
    """Log email notification."""
    logger.info(
        "Email notification sent",
        extra={
            "to_email": to_email,
            "alert_id": alert_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def log_scan_completed(total_cases: int, newly_eligible: int, duration: float):
    """Log scan completion."""
    logger.info(
        "Scan completed",
        extra={
            "total_cases_scanned": total_cases,
            "newly_eligible_found": newly_eligible,
            "duration_seconds": duration,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def log_error(error_type: str, error_message: str, context: dict = None):
    """Log errors with context."""
    extra_data = {
        "error_type": error_type,
        "error_message": error_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    if context:
        extra_data.update(context)
    
    logger.error("Error occurred", extra=extra_data)