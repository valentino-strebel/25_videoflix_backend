# core/email_backends.py

import logging
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

logger = logging.getLogger(__name__)


class MultiEmailBackend:
    """
    Sends every email to both:
    - console backend
    - smtp backend

    In development, if SMTP fails (e.g. fake host), we log the error
    but do NOT crash the request.
    """

    def __init__(self, *args, **kwargs):
        self.console_backend = ConsoleBackend(*args, **kwargs)
        self.smtp_backend = SMTPBackend(*args, **kwargs)

    def send_messages(self, email_messages):
        console_count = self.console_backend.send_messages(email_messages)

        try:
            smtp_count = self.smtp_backend.send_messages(email_messages)
        except Exception as e:
            logger.error("SMTP send failed, falling back to console-only: %s", e)
            smtp_count = 0

        return console_count + smtp_count
