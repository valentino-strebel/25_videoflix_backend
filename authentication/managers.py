"""
Custom user manager for handling user and superuser creation.
"""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager for the custom User model.
    Provides logic for creating regular users and superusers,
    ensuring proper validation and default field values.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.

        Args:
            email (str): User's email address.
            password (str): Raw password to be hashed and stored.
            extra_fields (dict): Additional model fields.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If no email is provided.
        """
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean(exclude=["password"])
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create a regular user with no staff or superuser privileges.

        Args:
            email (str): User's email address.
            password (str | None): Raw password for the user.
            extra_fields (dict): Additional model fields.

        Returns:
            User: The created regular user.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create a superuser with all permissions enabled.

        Args:
            email (str): Superuser's email address.
            password (str): Raw password for the superuser.
            extra_fields (dict): Additional model fields.

        Returns:
            User: The created superuser.

        Raises:
            ValueError: If required superuser flags are not set.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
