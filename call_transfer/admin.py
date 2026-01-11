from django.contrib import admin
from call_transfer.models import TransferContact, TransferCondition,CallTransfer

# Register your models here.
admin.site.register(TransferCondition)
admin.site.register(TransferContact)
admin.site.register(CallTransfer)
