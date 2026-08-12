import smtplib
from email.message import EmailMessage
from config import SMTP_HOST


def send_email_alert(to_address: str, case_id: str, reason: str) -> bool:
    if not SMTP_HOST:
        print(f"[MOCK EMAIL] To: {to_address} | Case {case_id}: {reason}")
        return True
    msg = EmailMessage()
    msg["Subject"] = f"Bail Reckoner: case {case_id} now eligible"
    msg["From"] = "no-reply@bail-reckoner.local"
    msg["To"] = to_address
    msg.set_content(reason)
    with smtplib.SMTP(SMTP_HOST) as server:
        server.send_message(msg)
    return True
