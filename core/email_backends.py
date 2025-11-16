from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend


class MultiEmailBackend:
    """
    Sends every email to both:
    - console backend
    - smtp backend
    """

    def __init__(self, **kwargs):
        self.console_backend = ConsoleBackend(**kwargs)
        self.smtp_backend = SMTPBackend(**kwargs)

    def send_messages(self, email_messages):
        # 1. In Konsole ausgeben
        self.console_backend.send_messages(email_messages)

        # 2. Echte Mails senden
        return self.smtp_backend.send_messages(email_messages)
