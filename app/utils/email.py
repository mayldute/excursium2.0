import logging
import smtplib
import asyncio
from functools import partial

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

# Logger for email-related operations
logger = logging.getLogger(__name__)


def _send_email_sync(to: str, subject: str, body: str) -> None:
    """Send an email synchronously using SMTP over SSL.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The HTML content of the email.

    Returns:
        None

    Raises:
        smtplib.SMTPException: If the email sending fails due
            to SMTP server issues.
    """
    # Create email message
    message = MIMEMultipart()
    message["From"] = settings.smtp.from_email
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    # Connect to SMTP server and send email
    try:
        with smtplib.SMTP_SSL(
            settings.smtp.smtp_server, int(settings.smtp.smtp_port)
        ) as server:
            server.login(
                settings.smtp.smtp_username, settings.smtp.smtp_password
            )
            server.send_message(message)
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email to {to}: {e}")
        raise


async def send_email(to: str, subject: str, body: str) -> None:
    """Send an email asynchronously without blocking the event loop.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The HTML content of the email.

    Returns:
        None

    Raises:
        smtplib.SMTPException: If the email sending fails due
            to SMTP server issues.
    """
    # Run synchronous email sending in executor
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, partial(_send_email_sync, to, subject, body)
    )
