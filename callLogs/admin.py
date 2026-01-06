from django.contrib import admin
from callLogs.models import CallSession, CallTranscript

# Register your models here.
admin.site.register(CallSession)
admin.site.register(CallTranscript)
