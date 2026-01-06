from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from accounts.utils import generate_otp, human_readable_time_ago


class UserSerializer(serializers.ModelSerializer):
    last_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "last_active"]
        read_only_fields = ["id", "email", "first_name", "last_name", "last_active"]

    def get_last_active(self, obj):
        return human_readable_time_ago(obj.last_login)


class SelfProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "state_location",
            "role",
        ]
        read_only_fields = ["id", "email", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "state_location", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

        # send_otp_email(user.email)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found")
        return value

    def save(self):
        email = self.validated_data["email"]
        otp = generate_otp()

        cache.set(f"pwd_reset_otp_{email}", otp, timeout=300)

        # send_otp_email(email, otp)
        print("OTP:", otp)  # dev only


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        email = data["email"]
        otp = data["otp"]

        cached_otp = cache.get(f"pwd_reset_otp_{email}")

        if not cached_otp:
            raise serializers.ValidationError("OTP expired")

        if cached_otp != otp:
            raise serializers.ValidationError("Invalid OTP")

        return data

    def save(self):
        email = self.validated_data["email"]

        cache.delete(f"pwd_reset_otp_{email}")
        cache.set(f"pwd_reset_verified_{email}", True, timeout=600)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check if passwords match
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        # Check if OTP was verified
        verified = cache.get(f"pwd_reset_verified_{data['email']}")
        if not verified:
            raise serializers.ValidationError("OTP not verified or expired")

        return data

    def save(self):
        email = self.validated_data["email"]
        new_password = self.validated_data["new_password"]

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # Delete OTP verified flag after password reset
        cache.delete(f"pwd_reset_verified_{email}")

        return user
