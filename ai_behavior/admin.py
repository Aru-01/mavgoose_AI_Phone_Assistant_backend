from django.contrib import admin
from ai_behavior.models import (
    AIConfig,
    AutoTransferKeyword,
    BusinessHour,
    GreetingConfig,
)

# Register your models here.
admin.site.register(AIConfig)
admin.site.register(GreetingConfig)
admin.site.register(BusinessHour)
admin.site.register(AutoTransferKeyword)
