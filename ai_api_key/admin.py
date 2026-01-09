from django.contrib import admin
from ai_api_key.models import (
    APIKey,
    Model_Configuration,
    Speech_to_Text,
)

# Register your models here.
admin.site.register(APIKey)
admin.site.register(Model_Configuration)
admin.site.register(Speech_to_Text)
