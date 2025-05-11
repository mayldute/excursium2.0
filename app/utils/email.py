import smtplib
import asyncio
from functools import partial
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")


def _send_email_sync(to: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = FROM_EMAIL
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT)) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)

async def send_email(to: str, subject: str, body: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_send_email_sync, to, subject, body))