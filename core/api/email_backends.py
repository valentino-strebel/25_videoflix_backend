"""
Email backend that duplicates outgoing messages to both console and SMTP backends.
Useful for development environments where SMTP may fail without interrupting requests.
"""

import logging
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

logger = logging.getLogger(__name__)


class MultiEmailBackend:
    """
    Email backend that sends each message to both the console backend and the SMTP backend.
    If the SMTP backend fails (common during development), the error is logged and the
    application continues without raising an exception.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize console and SMTP email backends with the same configuration.

        Args:
            *args: Positional arguments passed to underlying backends.
            **kwargs: Keyword arguments passed to underlying backends.
        """
        self.console_backend = ConsoleBackend(*args, **kwargs)
        self.smtp_backend = SMTPBackend(*args, **kwargs)

    def send_messages(self, email_messages):
        """
        Send messages using both console and SMTP backends.

        Args:
            email_messages (list): List of EmailMessage instances to be sent.

        Returns:
            int: Total number of successfully sent messages across both backends.
        """
        console_count = self.console_backend.send_messages(email_messages)

        try:
            smtp_count = self.smtp_backend.send_messages(email_messages)
        except Exception as e:
            logger.error("SMTP send failed, falling back to console-only: %s", e)
            smtp_count = 0

        return console_count + smtp_count
