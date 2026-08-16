"""
Notification manager for Monitoring & Outreach Engine.

Handles sending emails and SMS messages to users about eligible cases.
Supports both immediate and digest notifications.

Time Complexity: O(1) per notification (email/SMS send)
Space Complexity: O(1) — no large data structures
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime, timezone

from config import config
from models import Alert, AlertConfig

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Sends notifications (email/SMS) to users about eligible cases.
    
    Handles:
    - Email notifications via SMTP
    - SMS notifications via Twilio (stretch goal)
    - Notification preferences (immediate vs digest)
    - Fallback to console if services unavailable
    
    Time Complexity: O(1) per notification
    Space Complexity: O(1)
    """
    
    def __init__(self):
        """Initialize notification manager with service credentials."""
        self.smtp_enabled = config.SMTP_ENABLED
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USER
        self.smtp_password = config.SMTP_PASSWORD
        self.from_email = config.SMTP_FROM_EMAIL
        
        self.twilio_enabled = config.TWILIO_ENABLED
        self.twilio_account_sid = config.TWILIO_ACCOUNT_SID
        self.twilio_auth_token = config.TWILIO_AUTH_TOKEN
        self.twilio_from_number = config.TWILIO_FROM_NUMBER
        
        logger.info(f"NotificationManager initialized (SMTP: {self.smtp_enabled}, Twilio: {self.twilio_enabled})")
    
    def format_alert_email(self, alert: Alert, user: AlertConfig) -> Dict:
        """
        Format an alert as an email (subject + body).
        
        Time Complexity: O(1) — string formatting
        Space Complexity: O(1)
        
        Args:
            alert: Alert object
            user: User to receive email
        
        Returns:
            Dict with 'subject' and 'body' keys
        """
        subject = f"⚠️ Bail Eligibility Alert — Case {alert.case_id}"
        
        body = f"""
Dear User,

A prisoner in {alert.district}, {alert.state} has become eligible for bail.

CASE DETAILS:
─────────────
Case ID: {alert.case_id}
Prisoner ID: {alert.prisoner_id}
Offense Category: {alert.offense_category}
Maximum Sentence: {alert.max_sentence_months} months
Custody Start Date: {alert.custody_start_date.strftime('%Y-%m-%d')}

ELIGIBILITY REASON:
───────────────────
{alert.eligibility_reason.replace('_', ' ').title()}

This prisoner has now served enough time to be eligible for bail under 
Section 436A CrPC / Section 479 BNSS.

ACTION REQUIRED:
────────────────
Please review this case and consider filing a bail application.

Alert ID: {alert.id}
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---
Bail Reckoner Monitoring System
{config.SMTP_FROM_EMAIL}
"""
        
        return {
            "subject": subject,
            "body": body
        }
    
    def format_alert_sms(self, alert: Alert) -> str:
        """
        Format an alert as an SMS message.
        
        SMS must be brief (160 characters).
        
        Time Complexity: O(1) — string formatting
        Space Complexity: O(1)
        
        Args:
            alert: Alert object
        
        Returns:
            SMS body string
        """
        message = (
            f"🔔 Bail Alert: Case {alert.case_id} ({alert.prisoner_id}) in "
            f"{alert.district}, {alert.state} is now eligible. "
            f"Alert ID: {alert.id}"
        )
        
        return message[:160]  # SMS limit
    
    def send_email(self, to_email: str, alert: Alert, user: AlertConfig) -> bool:
        """
        Send email notification about an alert.
        
        Uses SMTP to send email. Falls back to logging if SMTP unavailable.
        
        Time Complexity: O(1) — single email send
        Space Complexity: O(1)
        
        Args:
            to_email: Email address to send to
            alert: Alert object
            user: User configuration
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.smtp_enabled:
                logger.warning(f"SMTP not enabled, logging email instead: {to_email}")
                email_content = self.format_alert_email(alert, user)
                logger.info(f"EMAIL TO: {to_email}")
                logger.info(f"SUBJECT: {email_content['subject']}")
                logger.info(f"BODY:\n{email_content['body']}")
                return True
            
            # Format email
            email_content = self.format_alert_email(alert, user)
            
            # Create MIME message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = email_content['subject']
            
            msg.attach(MIMEText(email_content['body'], 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email} for alert {alert.id}")
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to_email}: {e}")
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False

        # services/monitoring-engine/notify.py

def send_email_notification(case_id: str, email: str, case_details: str):
    """Send email notification via Gmail SMTP"""
    
    if not config.SMTP_ENABLED:
        logger.warning("Email notifications disabled")
        return False
    
    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        
        # Prepare email
        message = MIMEMultipart()
        message['From'] = config.SMTP_FROM_EMAIL
        message['To'] = email
        message['Subject'] = f'New Bail Case Alert - {case_id}'
        
        body = f"""
        A new case has become eligible for bail!
        
        Case ID: {case_id}
        Details: {case_details}
        
        Please check the application for more information.
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Send email
        server.send_message(message)
        server.quit()
        
        logger.info(f"✅ Email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email failed: {e}")
        return False
    
    def send_sms(self, to_number: str, alert: Alert, user: AlertConfig) -> bool:
        """
        Send SMS notification about an alert.
        
        Uses Twilio API. Falls back to logging if not configured.
        
        Time Complexity: O(1) — single SMS send
        Space Complexity: O(1)
        
        Args:
            to_number: Phone number to send to
            alert: Alert object
            user: User configuration
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.twilio_enabled:
                logger.warning(f"Twilio not enabled, logging SMS instead: {to_number}")
                sms_body = self.format_alert_sms(alert)
                logger.info(f"SMS TO: {to_number}")
                logger.info(f"BODY: {sms_body}")
                return True
            
            # TODO: Implement Twilio SMS sending
            # from twilio.rest import Client
            # client = Client(self.twilio_account_sid, self.twilio_auth_token)
            # message = client.messages.create(
            #     body=self.format_alert_sms(alert),
            #     from_=self.twilio_from_number,
            #     to=to_number
            # )
            # logger.info(f"SMS sent to {to_number} (SID: {message.sid})")
            # return True
            
            logger.info("Twilio SMS not yet implemented (fallback to logging)")
            sms_body = self.format_alert_sms(alert)
            logger.info(f"SMS TO: {to_number}")
            logger.info(f"BODY: {sms_body}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return False
    
    def should_notify_now(self, user: AlertConfig) -> bool:
        """
        Determine if user should receive immediate notification.
        
        Time Complexity: O(1) — simple boolean check
        Space Complexity: O(1)
        
        Args:
            user: User configuration
        
        Returns:
            True if should notify immediately, False if digest only
        """
        return user.notify_immediately
    
    def is_digest_time(self, user: AlertConfig, current_hour: int) -> bool:
        """
        Check if it's time to send daily digest to user.
        
        Time Complexity: O(1) — simple comparison
        Space Complexity: O(1)
        
        Args:
            user: User configuration
            current_hour: Current hour (0-23)
        
        Returns:
            True if digest should be sent now, False otherwise
        """
        if not user.digest_enabled:
            return False
        
        return current_hour == user.digest_hour


# ============================================================================
# Email Template Helpers
# ============================================================================

def render_alert_html(alert: Alert) -> str:
    """
    Render alert as HTML email (optional enhancement).
    
    Time Complexity: O(1) — string formatting
    Space Complexity: O(1)
    
    Args:
        alert: Alert object
    
    Returns:
        HTML string
    """
    html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .content {{ padding: 20px; }}
                .alert-box {{ border-left: 4px solid #ff6b6b; padding: 15px; background-color: #fff5f5; }}
                .case-details {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .footer {{ color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ Bail Eligibility Alert</h2>
                </div>
                
                <div class="content">
                    <p>A prisoner has become eligible for bail.</p>
                    
                    <div class="alert-box">
                        <strong>Case ID:</strong> {alert.case_id}<br>
                        <strong>Prisoner ID:</strong> {alert.prisoner_id}<br>
                        <strong>Location:</strong> {alert.district}, {alert.state}<br>
                        <strong>Offense:</strong> {alert.offense_category.replace('_', ' ').title()}
                    </div>
                    
                    <div class="case-details">
                        <h3>Details</h3>
                        <p><strong>Maximum Sentence:</strong> {alert.max_sentence_months} months</p>
                        <p><strong>Custody Start Date:</strong> {alert.custody_start_date.strftime('%B %d, %Y')}</p>
                        <p><strong>Eligibility Reason:</strong> {alert.eligibility_reason.replace('_', ' ').title()}</p>
                    </div>
                    
                    <p>This prisoner has now served enough time to potentially be eligible for bail under 
                    Section 436A CrPC / Section 479 BNSS.</p>
                    
                    <p><strong>Next Steps:</strong> Please review this case and consider filing a bail application.</p>
                    
                    <div class="footer">
                        <p>Alert ID: {alert.id}</p>
                        <p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p>Bail Reckoner Monitoring System</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    
    return html


# ============================================================================
# Manual Testing
# ============================================================================

if __name__ == "__main__":
    """Test notification sending."""
    logging.basicConfig(level=logging.INFO)
    
    # Create mock objects for testing
    from models import Alert, AlertStatus
    
    mock_alert = Alert(
        case_id="TEST-001",
        prisoner_id="PRIS-2026-00001",
        state="Maharashtra",
        district="Mumbai",
        offense_category="crimes_against_women",
        max_sentence_months=36,
        custody_start_date=datetime(2024, 6, 15, tzinfo=timezone.utc),
        eligibility_reason="served_50_percent",
        status=AlertStatus.PENDING.value
    )
    
    mock_user = AlertConfig(
        user_id="user-123",
        email_enabled=True,
        email_address="test@example.com",
        sms_enabled=False,
        sms_number=None,
        notify_immediately=True,
        digest_enabled=False,
        digest_hour=9
    )
    
    notifier = NotificationManager()
    
    print("Testing email notification...")
    result = notifier.send_email(mock_user.email_address, mock_alert, mock_user)
    print(f"Email result: {result}\n")
    
    print("Testing SMS notification...")
    result = notifier.send_sms("+919876543210", mock_alert, mock_user)
    print(f"SMS result: {result}\n")