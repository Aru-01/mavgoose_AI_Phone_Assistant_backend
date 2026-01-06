from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.managers import CustomUserManager


# Create your models here.
class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    STORE_MANAGER = "STORE_MANAGER", "Store Manager"
    STAFF = "STAFF", "Staff"


class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    state_location = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.STAFF
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
