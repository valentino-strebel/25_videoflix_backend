"""
Token generators for account activation and password reset functionality.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token generator used for email-based account activation.
    Inherits all behavior from Django's PasswordResetTokenGenerator.
    """
    pass


activation_token_generator = ActivationTokenGenerator()
password_reset_token_generator = PasswordResetTokenGenerator()
