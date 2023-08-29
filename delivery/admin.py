from django.contrib import admin
from .models import Delivery, DeliveryAgent, PickDrop


class DeliveryAgentModelAdmin(admin.ModelAdmin):
    ordering = ['available']

class DeliveyModelAdmin(admin.ModelAdmin):
    ordering = ['-delivery_status']
    pass
        

# Register your models here.
admin.site.register(Delivery, DeliveyModelAdmin)
admin.site.register(DeliveryAgent, DeliveryAgentModelAdmin)
admin.site.register(PickDrop)

