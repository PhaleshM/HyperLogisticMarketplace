from django.db import models
from seller.models import Product, Listing,SellerProfile
from account.models import User
from phonenumber_field.modelfields import PhoneNumberField
from account.models import Address
from decimal import Decimal
# from delivery.models import Delivery, DeliveryAgent

def profile_pic_upload_path(instance, filename):
    # Define the upload path for the profile picture
    # Use the filename as it is
    return f'profile_pic/{filename}'

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
    phone_number = PhoneNumberField(max_length = 13, default = '')
    address = models.ForeignKey(Address, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    profile_picture = models.ImageField(
        upload_to = profile_pic_upload_path,
        blank = True,
        null = True,
        default = '/Sameep/media/profile_pic/default_user.jpg'
    )  # Stores the profile picture of the customer 
    wishlist = models.ManyToManyField(Listing, blank = True)  # Many-to-many relationship with Product for storing wishlist items


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,default=None)
    items = models.ManyToManyField(Listing, through='CartItem')

    def add_to_cart(self, listing, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(cart=self, listing=listing)
        cart_item.quantity += quantity
        cart_item.save()

    def remove_from_cart(self, listing):
        CartItem.objects.filter(cart=self, listing=listing).delete()

    @staticmethod
    def create_cart_for_user(user):
        return Cart.objects.create(user=user)

    def __str__(self):
        return str(self.user)
    

    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.item)
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    PAYMENT_CHOICES=(
        ('online','Online'),
        ('offline','Offline'),
    )

    order_id = models.AutoField(primary_key=True, editable=False)
    seller=models.ForeignKey(SellerProfile,on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    total_quantity=models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits = 10, decimal_places = 2, default=Decimal('0.00'))  # Total amount of the order
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_mode=models.CharField(max_length=20,choices=PAYMENT_CHOICES,default='offline')
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_time = models.DateTimeField(blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True)
    return_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate the order ID when the order is created
            last_order = Order.objects.order_by('-order_id').first()
            if last_order:
                self.order_id = last_order.order_id + 1
            else:
                self.order_id = 0000000000

            # Calculate the total quantity and total amount based on the items in the order
            self.total_quantity = sum(item.quantity for item in self.items.all())
            
        super().save(*args, **kwargs)

    # order is cancelled due to some technical or managerial issues
    def cancel_order(self, reason=None):
        self.status = 'CANCELLED'
        self.cancellation_reason = reason
        self.save()
    
    def __str__(self):
        return f"Order {self.customer}"
    



class Comment(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.PROTECT, related_name='comments')
    text = models.TextField(default='')  # Text of the comment
    products = models.ForeignKey(Product, on_delete=models.PROTECT,default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.customer.user}"

class ReturnProduct(models.Model):
    #the product that is being returned
    foul_product = models.ForeignKey(Listing, on_delete=models.PROTECT)

    