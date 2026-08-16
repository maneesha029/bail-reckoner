# test_notifications.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
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
Hi there! 👋

This is a TEST email from the Bail Reckoner system.

If you're seeing this, it means:
✅ Email configuration is working!
✅ Gmail is properly configured!
✅ Real notifications will be sent when cases are found!

Case Details:
- Case ID: TEST-001
- Status: Test Case
- Action: This is just a test

The system is ready to send real notifications!

Best regards,
Bail Reckoner Monitoring Engine
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Send email
        server.send_message(message)
        server.quit()
        
        print(f"✅ Test email sent successfully to {recipient_email}!")
        print("Check your inbox in 1-2 seconds")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

