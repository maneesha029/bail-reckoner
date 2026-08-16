"""
Celery scheduler for Monitoring & Outreach Engine.

Handles periodic scanning for newly eligible cases and alert creation.

Time Complexity: O(n) where n = number of undertrial cases
Space Complexity: O(n) for storing eligible cases in memory
"""
import logging
from retry_utils import retry_with_backoff
from logging_config import log_alert_created, log_scan_completed, log_error
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import config
from models import Alert, AlertConfig, AlertStatus, Base
from notify import NotificationManager

logger = logging.getLogger(__name__)


class CaseMonitoringScanner:
    def __init__(self):
        """Initialize scanner with database and service URLs."""
        self.eligibility_service_url = config.ELIGIBILITY_SERVICE_URL
        self.trust_service_url = config.TRUST_SERVICE_URL
        self.database_url = config.DATABASE_URL
        
        # Setup database session
        engine = create_engine(self.database_url)
        SessionLocal = sessionmaker(bind=engine)
        self.db = SessionLocal()
        
        # Setup notification manager
        self.notifier = NotificationManager()
        
        logger.info("CaseMonitoringScanner initialized")

    @retry_with_backoff(max_retries=3, backoff_seconds=1)
    def get_all_undertrial_cases(self) -> List[Dict]:
        """Fetch all undertrial cases from Member 1's service."""
        try:
            logger.info("Fetching all undertrial cases from Member 1...")
            
            url = f"{self.eligibility_service_url}/api/v1/cases/under_trial"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            cases = response.json()
            logger.info(f"Fetched {len(cases)} undertrial cases")
            return cases
        
        except requests.RequestException as e:
            log_error("API_ERROR", f"Failed to fetch cases from Member 1: {e}", {
                "service": "Member 1",
                "endpoint": "/api/v1/cases/under_trial"
            })
            raise
    
    @retry_with_backoff(max_retries=3, backoff_seconds=1)
    def check_case_eligibility(self, case_id: str) -> Optional[Dict]:
        """Check if a single case is eligible for bail."""
        try:
            url = f"{self.eligibility_service_url}/api/v1/eligibility/check/{case_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") == "eligible_now":
                return result
            
            return None
        
        except requests.RequestException as e:
            log_error("API_ERROR", f"Failed to check eligibility for case {case_id}: {e}", {
                "case_id": case_id,
                "service": "Member 1"
            })
            raise
    
    def create_alert(self, case_info: Dict, eligibility_info: Dict) -> Optional[Alert]:
        """Create an alert record for an eligible case."""
        try:
            alert = Alert(
                case_id=case_info.get("case_id"),
                prisoner_id=case_info.get("prisoner_id"),
                state=case_info.get("state"),
                district=case_info.get("district"),
                offense_category=case_info.get("charges", [{}])[0].get("offense_category", "general"),
                max_sentence_months=case_info.get("charges", [{}])[0].get("max_sentence_months", 0),
                custody_start_date=datetime.fromisoformat(
                    case_info.get("custody_start_date").replace("Z", "+00:00")
                ),
                eligibility_reason=eligibility_info.get("reason", "served_threshold"),
                date_became_eligible=datetime.now(timezone.utc),
                status=AlertStatus.PENDING.value,
                created_by="system"
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            # ✅ LOG ALERT CREATION
            log_alert_created(
                case_id=alert.case_id,
                alert_id=str(alert.id),
                prisoner_id=alert.prisoner_id,
                state=alert.state,
                district=alert.district
            )
            
            return alert
        
        except Exception as e:
            log_error("DB_ERROR", f"Failed to create alert for case {case_info.get('case_id')}: {e}", {
                "case_id": case_info.get("case_id")
            })
            self.db.rollback()
            return None
    
    def run_scan(self) -> Dict:
        """Main scan loop: find eligible cases and create alerts."""
        import time
        start_time = time.time()
        
        logger.info("Starting case eligibility scan...")
        
        stats = {
            "total_cases_scanned": 0,
            "newly_eligible_found": 0,
            "newly_flagged": 0,
            "skipped_already_flagged": 0,
            "notification_errors": 0,
            "errors": []
        }
        
        try:
            # Get all undertrial cases
            cases = self.get_all_undertrial_cases()
            stats["total_cases_scanned"] = len(cases)
            
            if not cases:
                logger.warning("No undertrial cases found")
                return stats
            
            # Check each case for eligibility
            for case in cases:
                case_id = case.get("case_id")
                
                try:
                    # Check if already flagged
                    if self.is_already_flagged(case_id):
                        stats["skipped_already_flagged"] += 1
                        continue
                    
                    # Check eligibility
                    eligibility_info = self.check_case_eligibility(case_id)
                    if not eligibility_info:
                        continue
                    
                    stats["newly_eligible_found"] += 1
                    
                    # Create alert
                    alert = self.create_alert(case, eligibility_info)
                    if not alert:
                        stats["errors"].append(f"Failed to create alert for {case_id}")
                        continue
                    
                    stats["newly_flagged"] += 1
                    
                    # Log to audit
                    self.log_to_audit(alert, "alert_created")
                    
                    # Notify users
                    users = self.get_users_for_notification(case.get("state"), case.get("district"))
                    if users:
                        notified = self.notify_users(alert, users)
                        logger.info(f"Notified {notified} users for alert {alert.id}")
                
                except Exception as e:
                    log_error("SCAN_ERROR", f"Error processing case {case_id}: {e}", {
                        "case_id": case_id
                    })
                    stats["errors"].append(f"Error processing case {case_id}: {str(e)}")
            
            elapsed = time.time() - start_time
            stats["scan_duration_seconds"] = elapsed
            
            # ✅ LOG SCAN COMPLETION
            log_scan_completed(
                total_cases=stats["total_cases_scanned"],
                newly_eligible=stats["newly_eligible_found"],
                duration=elapsed
            )
            
            logger.info(f"Scan completed in {elapsed:.2f}s: {stats}")
            return stats
        
        except Exception as e:
            log_error("SCAN_FAILED", f"Scan failed: {e}")
            stats["errors"].append(f"Scan failed: {str(e)}")
            return stats
        
        finally:
            self.db.close()


# ============================================================================
# Celery Task (if using Celery)
# ============================================================================

#TODO: Uncomment when Celery is configured
from celery import Celery
 
celery_app = Celery(
    'monitoring_engine',
    broker=config.REDIS_URL,
    backend=config.REDIS_URL
)
 
@celery_app.task
def scan_for_eligible_cases():
    """Celery task to run the scanner periodically."""
    scanner = CaseMonitoringScanner()
    return scanner.run_scan()
 
 # Schedule the task
celery_app.conf.beat_schedule = {
    'scan-every-30-minutes': {
        'task': 'scheduler.scan_for_eligible_cases',
        'schedule': 30 * 60,  # 30 minutes in seconds
    },
}


# ============================================================================
# Manual Testing
# ============================================================================

if __name__ == "__main__":
    """Run scanner manually for testing."""
    logging.basicConfig(level=logging.INFO)
    
    scanner = CaseMonitoringScanner()
    results = scanner.run_scan()
    
    print("\n" + "="*80)
    print("SCAN RESULTS")
    print("="*80)
    print(f"Total cases scanned: {results['total_cases_scanned']}")
    print(f"Newly eligible found: {results['newly_eligible_found']}")
    print(f"New alerts created: {results['newly_flagged']}")
    print(f"Already flagged skipped: {results['skipped_already_flagged']}")
    print(f"Scan duration: {results.get('scan_duration_seconds', 0):.2f}s")
    
    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("="*80)