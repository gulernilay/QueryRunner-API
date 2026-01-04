"""
Mail Logger Utility

Provides a buffered logging system that accumulates log messages and sends them
via email to a list of recipients. Useful for audit trails, error notifications
and request/response logging in production environments.

Exports:
- MailLogger (class)
    Class-level methods to manage a message buffer, associate it with an endpoint,
    and send the accumulated log as an email to configured recipients.

Usage:
    MailLogger.start("/auth/login")
    MailLogger.add("User authentication attempt")
    MailLogger.add("Token generated successfully")
    MailLogger.send()  # Sends buffered messages to all recipients

Notes:
- Messages are buffered in memory until send() is called.
- Each email includes the endpoint name in the subject line.
- All recipients receive the same email content.
"""
from utils.send_mail import send_mail
import os
from dotenv import load_dotenv

load_dotenv()


class MailLogger:
    """Buffered email logging system for API audit trails and notifications.
    
    Class Attributes:
        buffer (list): In-memory buffer of log messages.
        endpoint (str): Current endpoint being logged (for email subject).
        recipients (list): Email addresses to receive log messages, loaded from .env.
    """

    buffer = []
    endpoint = ""

    raw_recipients = os.getenv("MAIL_RECIPIENTS", "")
    recipients = [r.strip() for r in raw_recipients.split(",") if r.strip()]

    @classmethod
    def start(cls, endpoint: str):
        """Initialize logging for a specific endpoint."""
        cls.endpoint = endpoint
        cls.buffer = []

    @classmethod
    def add(cls, message: str):
        """Add a message to the log buffer."""
        cls.buffer.append(message)

    @classmethod
    def send(cls):
        """Send accumulated log messages to all configured recipients."""
        if len(cls.buffer) == 0:
            return

        full_message = "\n".join(cls.buffer)

        for recipient in cls.recipients:
            send_mail(
                to_email=recipient,
                subject=f"QueryRunner Log - {cls.endpoint}",
                message=full_message
            )