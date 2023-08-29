from django.db import models
from account.models import User, Region
from buyer.models import Order
from phonenumber_field.modelfields import PhoneNumberField
import random


# Create your models here.

class DeliveryAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(max_length=13, default='')
    # profile pic
    aadhar_number = models.CharField(max_length=255)
    adhar_front = models.ImageField(
        upload_to = 'delivery/delivery_agent_docs/', 
        default = "", 
        )
    adhar_back = models.ImageField(
        upload_to = 'delivery/delivery_agent_docs/', 
        default = "", 
        )
    PAN_number = models.CharField(max_length=255)
    PAN_front = models.ImageField(
        upload_to = 'delivery/delivery_agent_docs/', 
        default = "", 
        )
    driving_licence = models.CharField(max_length=255)
    driving_licence_front = models.ImageField(
        upload_to = 'delivery/delivery_agent_docs/', 
        default = "", 
        )
    vehicle_number = models.CharField(max_length=255)
    number_plate = models.ImageField(
        upload_to = 'delivery/delivery_agent_docs/', 
        default = "", 
        )
    available = models.BooleanField(default=True)
    #change it to arrayfield for postgres
    delivery_regions = models.ManyToManyField(Region, related_name='delivery_agents')       #many to many fild is given so that one delivey agent may have more than one region to cover
    delivery_count = models.IntegerField(default=0)


    def __str__(self):
        return self.name

    def generate_otp():
        """
        Generate a 4-digit OTP (One-Time Password).
        """
        return random.randint(1000, 9999)
    
    

class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.PROTECT)
    # delivery_status_choices = (
    #     ('PENDING', 'Pending'),
    #     ('IN_TRANSIT', 'In Transit'),
    #     ('DELIVERED', 'Delivered')
    # )
    delivery_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='PENDING')   
    is_picked = models.BooleanField(default=False)
    #otp = models.PositiveIntegerField(generate_otp(),verbose_name=('OTP'), help_text=('One-time password for delivery confirmation'),)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery {self.id} - {self.order}"

    def delivered():
        if Delivery.is_delivered == True:
            DeliveryAgent.delivery_count += 1

        
    def select_delivery_agent(order):
        # Get the region of the seller associated with the order
        seller_region = order.seller.address.region
        # Find available delivery agents in the same region
        available_agents = DeliveryAgent.objects.filter(is_available=True, region=seller_region)
        # Select a delivery agent based on your preferred criteria (e.g., random selection, first available)
        selected_agent = available_agents.first()  # Example: Select the first available agent

        return selected_agent

class PickDrop(models.Model):
    weight_choices = (
        ('0kg to 2kg', '2'),
        ('2kg to 5kg', '5'),
        ('5kg to 6kg', '6'),
        ('6kg to 7kg', '7'),
        ('7kg to 8kg', '8'),
        ('8kg to 9kg', '9'),
        ('9kg to 10kg', '10'),
    )
    #delivery charges 50 rupees for first 3 km then 10 rupee per km
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pick_up_address = models.CharField(max_length=255)
    pick_up_phone_number = PhoneNumberField(max_length=13, default='')
    drop_phone_number = PhoneNumberField(max_length=13, default='')
    drop_address = models.CharField(max_length=255)
    weight = models.CharField(choices = weight_choices, max_length=15)
    description = models.CharField(max_length=500, default='')

    