from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.managers import CustomUserManager
from store.models import Store


# Create your models here.
class UserRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    STORE_MANAGER = "STORE_MANAGER", "Store Manager"
    STAFF = "STAFF", "Staff"


class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    state_location = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.STAFF
    )
    profile_image = models.ImageField(upload_to="users/profile/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
