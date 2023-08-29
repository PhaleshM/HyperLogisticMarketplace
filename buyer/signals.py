# signals.py
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart,CustomerProfile

@receiver(post_save, sender=CustomerProfile)
def create_cart_for_new_customer(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance.user)