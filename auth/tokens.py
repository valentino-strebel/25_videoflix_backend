from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    pass


activation_token_generator = ActivationTokenGenerator()
password_reset_token_generator = PasswordResetTokenGenerator()
