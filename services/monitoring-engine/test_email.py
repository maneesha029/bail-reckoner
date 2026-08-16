# test_email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config

def test_email():
    """Test email configuration"""
    
    try:
        print("📧 Testing Email Configuration...")
        print(f"SMTP Server: {config.SMTP_HOST}:{config.SMTP_PORT}")
        print(f"From: {config.SMTP_USER}")
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
        print("✅ Connected to SMTP server")
        
        # Enable TLS encryption
        server.starttls()
        print("✅ TLS enabled")
        
        # Login to Gmail
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        print("✅ Logged in successfully")
        
        print("\n✅ Email configuration is valid!")
        print("Ready to send emails!")
        
        server.quit()
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ Authentication failed!")
        print(f"Exact Gmail error: {e}")
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_email()