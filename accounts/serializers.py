from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from accounts.utils import human_readable_time_ago, send_otp_email


class UserSerializer(serializers.ModelSerializer):
    last_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "store",
            "profile_image",
            "last_active",
            "password",
        ]
        read_only_fields = ["id", "last_active"]
        extra_kwargs = {
            "password": {"write_only": True},
            "profile_image": {"required": False},
        }

    def get_last_active(self, obj):
        if not obj.last_login:
            return "Never active"
        diff = (timezone.now() - obj.last_login).total_seconds()
        if diff < 60:
            return "Active now"
        return human_readable_time_ago(obj.last_login)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class SelfProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "state_location",
            "role",
        ]
        read_only_fields = ["id", "email", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "state_location",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

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

        send_otp_email(email)
        # print("OTP:", otp)  # dev only


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


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found")
        return value

    def save(self):
        email = self.validated_data["email"]
        cooldown_key = f"pwd_reset_resend_{email}"

        # Check if user can resend OTP (30 sec cooldown)
        if cache.get(cooldown_key):
            raise serializers.ValidationError(
                "OTP recently sent. Please wait 30 seconds before resending."
            )

        # Send OTP again
        send_otp_email(email)

        # Set 30 sec cooldown
        cache.set(cooldown_key, True, timeout=30)
