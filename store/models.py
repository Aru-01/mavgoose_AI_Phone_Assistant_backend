from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.TextField()
    manager_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
