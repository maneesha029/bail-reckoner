# test_email_notifications_only.py
# Email-only notifications testing (SMS removed)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config

def send_test_email(recipient_email: str):
    """Send a test email to yourself"""
    
    try:
        print(f"📧 Sending test email to {recipient_email}...")
        
        # Connect to Gmail
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        
        # Create email
        message = MIMEMultipart()
        message['From'] = config.SMTP_USERNAME
        message['To'] = recipient_email
        message['Subject'] = '🎉 Test Email from Bail Reckoner'
        
        body = """
Dear User,

This is a TEST email from the Bail Reckoner Monitoring Engine.

If you're seeing this, it means:
✅ Email configuration is working!
✅ Gmail is properly configured!
✅ Real notifications will be sent when eligible cases are found!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST CASE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case ID: TEST-001
Status: Test Case
Action: This is just a test notification

The system is now ready to send real email alerts when bail-eligible 
cases are identified!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
Bail Reckoner Monitoring Engine

This is an automated test message.
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Send email
        server.send_message(message)
        server.quit()
        
        print(f"✅ Test email sent successfully to {recipient_email}!")
        print("Check your inbox in 1-2 seconds")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("BAIL RECKONER - EMAIL NOTIFICATION TEST (EMAIL ONLY)")
    print("=" * 70)
    
    # Get email from user
    your_email = input("\n📧 Enter your email to test: ")
    
    print("\nStarting email test...\n")
    
    # Test email
    if config.SMTP_ENABLED:
        success = send_test_email(your_email)
        if success:
            print("\n" + "=" * 70)
            print("✅ EMAIL TEST COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\nEmail sent to: {your_email}")
            print("Check your inbox for the test message")
            print("\n" + "=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ EMAIL TEST FAILED")
            print("=" * 70)
            print("\nPossible reasons:")
            print("1. Gmail authentication failed - check SMTP_USERNAME and SMTP_PASSWORD in .env")
            print("2. SMTP server connection failed - check SMTP_SERVER and SMTP_PORT")
            print("3. 2FA not enabled on Gmail - must enable 2FA and use app password")
            print("\nFor setup help, see EMAIL_SMS_SETUP_COMPLETE_GUIDE.md")
            print("=" * 70)
    else:
        print("⚠️  Email is disabled in config (.env)")
        print("Set: SMTP_ENABLED=true")
        print("=" * 70)