from typing import List
import logging
import os
from sendgrid import SendGridAPIClient, Mail

sendgrid_token = os.getenv("SENDGRID_TOKEN")

logging.getLogger().setLevel(logging.INFO)


def send_mail(from_email: str, to_emails: List, subject: str, mail_html_content: str):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=mail_html_content
    )
    sg = SendGridAPIClient(sendgrid_token)
    sg.send(message)
    logging.info(f"Mail send to {to_emails}")

