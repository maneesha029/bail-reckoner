# notify_email_only.py
# Email-only notifications (SMS/Twilio removed)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config
import logging

logger = logging.getLogger(__name__)

def send_email_notification(case_id: str, email: str, case_details: str = None):
    """Send email notification for a new alert"""
    
    if not config.SMTP_ENABLED:
        logger.warning("Email notifications disabled")
        return False
    
    try:
        logger.info(f"📧 Sending email notification for case {case_id} to {email}")
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        
        # Create email message
        message = MIMEMultipart()
        message['From'] = config.SMTP_USERNAME
        message['To'] = email
        message['Subject'] = f'🎉 New Eligible Bail Case Alert - {case_id}'
        
        # Email body
        body = f"""
Dear User,

A new case has become eligible for bail under Section 436A CrPC!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CASE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case ID: {case_id}
Status: ELIGIBLE FOR BAIL
Legal Basis: Section 436A CrPC (Criminal Procedure Code)

{case_details if case_details else 'Please check the Bail Reckoner application for complete details.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please log in to the Bail Reckoner application immediately to:
1. Review the case details
2. Check the eligibility criteria
3. Take necessary action for bail proceedings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ABOUT THIS ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from the Bail Reckoner Monitoring Engine.
It identifies undertrial cases that meet the eligibility criteria for bail
under Section 436A CrPC and Section 479 BNSS (Bharatiya Nyaya Sanhita).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
Bail Reckoner Monitoring Engine
Legal Tech System

This is an automated message. Please do not reply to this email.
For support, contact the Bail Reckoner team.
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Send email
        server.send_message(message)
        server.quit()
        
        logger.info(f"✅ Email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Email authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending email: {e}")
        return False


def send_alert_notification(case_id: str, email: str, state: str = None, district: str = None):
    """
    Send alert notification for eligible case
    
    Args:
        case_id: Case identifier
        email: Recipient email address
        state: State of the case (optional)
        district: District of the case (optional)
    
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    
    case_details = f"State: {state}\nDistrict: {district}" if state and district else None
    return send_email_notification(case_id, email, case_details)


if __name__ == "__main__":
    # Test email notification
    print("=" * 60)
    print("BAIL RECKONER - EMAIL NOTIFICATION TEST")
    print("=" * 60)
    
    test_email = input("\n📧 Enter your email to test: ")
    test_case_id = input("Enter test case ID (or press Enter for default): ") or "TEST-001"
    
    print(f"\nSending test email to {test_email}...")
    success = send_email_notification(
        case_id=test_case_id,
        email=test_email,
        case_details="This is a test notification from Bail Reckoner"
    )
    
    if success:
        print("✅ Test email sent successfully!")
        print("Check your inbox in 1-2 seconds")
    else:
        print("❌ Failed to send test email")
        print("Check your email configuration in .env file")
    
    print("=" * 60)