from django.db import models
from account.models import User
from phonenumber_field.modelfields import PhoneNumberField
from account.models import Address
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.utils import timezone
from decimal import Decimal
from .bankapi import get_bank_name
# Create your models here.

class Categories(models.Model):
    name = models.CharField(max_length=255, default='')  # Name of the category
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # Parent category (self-referencing relationship)
    logo = models.ImageField(
        upload_to = 'Categories_logos',
        blank = True, 
        null = True,
        default = '')  # Logo of the category
    returnable = models.BooleanField(default=False)
    replacable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    slug = models.SlugField()  # Slug field for SEO-friendly URLs
    
    class Meta:
        ordering = ('name',)  # Ordering the categories by name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'  # URL of the category

class Brand(models.Model):
    name = models.CharField(max_length=255, primary_key=True)  # Name of the brand
    slug = models.SlugField()  # Slug field for SEO-friendly URLs
    logo = models.ImageField(upload_to='Brand_logos', blank=True, null=True, default='')  # Logo of the brand
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)  # Ordering the brands by name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'  # URL of the brand
    
class Subscription(models.Model):
    plan_name = models.CharField(max_length=255, default='')  # Name of the subscription plan
    price = models.DecimalField(max_digits=8, decimal_places=2)  # Price of the subscription plan
    duration = models.IntegerField(default=0)  # Duration of the subscription plan in days
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plan_name

def seller_logo_upload_path(instance, filename):
    # Define the upload path for the seller logo
    # Use the user's username and the original filename
    return f'shop_logos/{instance.user}/{filename}'



class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # User associated with the seller profile
    shop_name = models.CharField(max_length=255, default='')  # Name of the shop
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(Categories,related_name='sellers',blank=False)  # Categories associated with the product
    phone_number = PhoneNumberField(max_length=13, default='')  # Phone number of the shop
    logo = models.ImageField(upload_to=seller_logo_upload_path, blank=True, null=True, default='')  # Logo of the shop
    description = models.CharField(max_length=800, default='', blank=True)  # Description of the shop
    gst = models.CharField(max_length=25, blank=True)
    acc_no=models.CharField( max_length=50,blank=True)
    ifsc_no=models.CharField( max_length=50,blank=True)
    bank_name=models.CharField(max_length=50,blank=True)
    benifichiery_name=models.CharField( max_length=50,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription = models.OneToOneField(Subscription, on_delete = models.PROTECT, null = True, blank = True)  # Subscription plan of the seller

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the created_at value when creating a new instance
            self.created_at = timezone.now()
        
        # Check if ifsc_no is provided and make a request to get bank_name
        if self.ifsc_no:
            bank_name = get_bank_name(self.ifsc_no)
            if bank_name is None:
                raise ValueError("Invalid IFSC number.")
            self.bank_name = bank_name
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.shop_name

def product_image_upload_path(instance, filename):
    # Define the upload path for the product images
    # Use the product_id and the original filename
    return f'product_images/{instance.product_id}/{filename}'

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)  # Unique identifier for the product
    name = models.CharField(max_length=255, default='')  # Name of the product
    description = models.TextField(null=True)  # Description of the product
    categories = models.ManyToManyField(Categories, related_name='products', blank=False)  # Categories associated with the product
    brand = models.ForeignKey(Brand, on_delete = models.PROTECT, null = True, blank = True, default = None)  # Brand of the product
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT)  # To get who registered the product
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_count = models.IntegerField(default=0)  # Number of orders for the product

    # Additional fields
    rating = models.FloatField(default=0.0)  # Rating of the product

    # @property
    # def average_rating(self):
    #     ratings = self.rating.all()
    #     count = ratings.count()
    #     if count > 0:
    #         total_rating = sum(rating.rating for rating in ratings)
    #         return total_rating / count
    #     return 0.0
    
    img1 = models.ImageField(
        upload_to = product_image_upload_path, 
        default = "", 
        null = True, 
        blank = True)  # Product image 1
    img2 = models.ImageField(
        upload_to = product_image_upload_path, 
        default = "", 
        null = True, 
        blank = True)  # Product image 2
    img3 = models.ImageField(
        upload_to = product_image_upload_path, 
        default = "", 
        null = True, 
        blank = True)  # Product image 3
    img4 = models.ImageField(
        upload_to = product_image_upload_path, 
        default = "", 
        null = True, 
        blank = True)  # Product image 4
    img5 = models.ImageField(
        upload_to = product_image_upload_path, 
        default = "", 
        null = True, 
        blank = True)  # Product image 5
    
    is_featured   = models.BooleanField(default=False)  # Indicates if the product is featured
    is_available  = models.BooleanField(default=True)  # Indicates if the product is available for purchase

    def __str__(self):
        return self.name
    
class Coupon(models.Model):
    code = models.CharField(max_length=255)
    description = models.TextField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0000'))
    start_date = models.DateField()
    end_date = models.DateField()
    # Add more fields for conditions if needed

    def is_valid(self, order):
        # Check conditions here
        # Example: Check if all items are groceries and total amount is more than 1000
        if order.items.filter(category='grocery').count() == order.items.count() and order.total_amount > 1000:
            return True
        return False


class Listing(models.Model):
    size_choices = (
        ('s', 'Small'),
        ('m', 'Medium'),
        ('l', 'Large'),
        ('xl', 'Extra Large'),
        ('xxl', 'Extra Extra Large'),
    )
    color_choices = (
        ('red', 'Red'),
        ('white', 'White'),
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('purple', 'Purple'),
        ('grey', 'Grey'),
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT)
    quantity= models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    size = models.CharField(choices=size_choices, blank=True,max_length=20)
    color = models.CharField(choices=color_choices, blank=True,max_length=20)
    #returnable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product}, {self.seller}"
    