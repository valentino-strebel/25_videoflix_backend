from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Handles user registration by validating email uniqueness and matching passwords.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        """
        Validates that both password fields match and that the email is not already in use.
        """
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError("Please check your input and try again.")
        return attrs

    def create(self, validated_data):
        """
        Creates a new user using the validated registration data.
        """
        email = validated_data["email"]
        password = validated_data["password"]
        user = User.objects.create_user(email=email, password=password)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Handles user authentication using email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        """
        Authenticates the user. Raises an error if credentials are invalid or account is inactive.
        """
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError("Please check your input and try again.")
        if not user.is_active:
            raise serializers.ValidationError("Account is not activated.")
        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """
    Accepts an email for initiating the password reset process.
    """
    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """
    Validates matching new password fields during password reset confirmation.
    """
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        """
        Ensures the new password and its confirmation match.
        """
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
