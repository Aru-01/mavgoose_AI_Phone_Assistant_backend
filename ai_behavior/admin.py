from django.contrib import admin
from ai_behavior.models import (
    AIBehaviorConfig,
    AutoTransferKeyword,
    BusinessHour,
    GreetingConfig,
)

# Register your models here.
admin.site.register(AIBehaviorConfig)
admin.site.register(GreetingConfig)
admin.site.register(BusinessHour)
admin.site.register(AutoTransferKeyword)
