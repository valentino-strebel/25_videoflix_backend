"""
Custom User model using email as the unique identifier.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    """
    User model that replaces the default username field with a unique email.
    Extends Django’s AbstractUser while removing the username field entirely.
    """

    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        Return the user's email as the string representation.
        """
        return self.email
