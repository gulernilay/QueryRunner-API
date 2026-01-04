"""

Provides email sending functionality via SMTP (Gmail). Used by MailLogger
to send audit logs, error notifications and request summaries to configured recipients.

Exports:
- send_mail(to_email: str, subject: str, message: str) -> None
    Send an email to a single recipient via Gmail SMTP server.

Configuration:
- MAIL_SENDER: Email address to send from (from .env file).
- MAIL_APP_PASSWORD: Gmail app password for authentication (from .env file).

Notes:
- Requires Gmail account with 2FA enabled and an app-specific password.
- Uses TLS encryption for SMTP connection security.
- Errors are caught and logged to console; no exceptions are raised to caller.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_mail(to_email: str, subject: str, message: str):
    """
    Send an email via Gmail SMTP server.
    
    Constructs an email message with the provided recipient, subject and body text,
    then connects to Gmail's SMTP server using TLS encryption and authentication
    credentials from environment variables. All operations are logged to console.

    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject line.
        message (str): Email body content (plain text, UTF-8 encoded).

    Returns:
        None

    Notes:
        - Sender address is read from MAIL_SENDER environment variable.
        - Authentication uses MAIL_APP_PASSWORD from environment (Gmail app-specific password).
        - On success, logs " Mail gönderildi: {to_email}".
        - On failure, logs " Mail gönderilemedi: {error}" and continues execution.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("MAIL_SENDER")
    password = os.getenv("MAIL_APP_PASSWORD")

    # Construct email message
    msg = MIMEMultipart()
    msg["From"] = f"Chef Seasons AI – QueryRunner API <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain", "utf-8"))

    try:
        # Connect to Gmail SMTP server with TLS encryption
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        print(f"📧 Mail gönderildi: {to_email}")
    except Exception as e:
        print(f"❌ Mail gönderilemedi: {e}")
