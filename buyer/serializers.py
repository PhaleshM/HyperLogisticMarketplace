from rest_framework import serializers
from account.models import User
from seller.models import SellerProfile
from phonenumbers import parse as parse_phone_number
from phonenumbers.phonenumberutil import is_valid_number, NumberParseException
from .models import CustomerProfile, CartItem, Comment, Product,Cart,Listing, Order
from account.serializers import AddressSerializer

# class CustomerProfileSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source='user.email', read_only=True)

#     class Meta:
#         model = CustomerProfile
#         fields = '__all__'
#         #fields = ['email', 'phone_number', 'address', 'profile_picture']

#     def validate_phone_number(self, value):
#         """
#         Custom validation for phone number field.
#         Ensure that the phone number is not already registered and is in the Indian region.
#         """
#         # Check if the phone number is already registered
#         if SellerProfile.objects.filter(phone_number=value).exists() and CustomerProfile.objects.filter(phone_number=value).exists():
#             raise serializers.ValidationError("This phone number is already registered.")

#         # Check if the phone number is in the Indian region and is valid
#         try:
#             parsed_number = parse_phone_number(value, "IN")
#             if not is_valid_number(parsed_number):
#                 raise serializers.ValidationError("The phone number entered is not valid for the Indian region.")
#         except NumberParseException:
#             raise serializers.ValidationError("The phone number entered is not valid.")

#         return value
    
# class CustomerProfileSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source='user.email', read_only=True)

#     class Meta:
#         model = CustomerProfile
#         fields = ['email', 'phone_number', 'profile_picture']

class CustomerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    # address_object = AddressSerializer(write_only=True)
    # address = AddressSerializer()

    def get_address(self, obj):
        address = obj.user.address
        return {
            'house': address.house,
            'street': address.street,
            # 'pin_code': address.pin_code,
            'city': address.city.name,
            'region': address.region.name,
            # 'pincode': address.region.pincode,
        }

    class Meta:
        model = CustomerProfile
        fields = ['email', 'phone_number', 'profile_picture']

    def validate_phone_number(self, value):
        """
        Custom validation for phone number field.
        Ensure that the phone number is not already registered and is in the Indian region.
        """
        # Check if the phone number is already registered
        if CustomerProfile.objects.filter(phone_number=value).exists() and CustomerProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")

        # Check if the phone number is in the Indian region and is valid
        try:
            parsed_number = parse_phone_number(value, "IN")
            if not is_valid_number(parsed_number):
                raise serializers.ValidationError("The phone number entered is not valid for the Indian region.")
        except NumberParseException:
            raise serializers.ValidationError("The phone number entered is not valid.")

        return value

class ViewCustomerProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = CustomerProfile
        fields = ['shop_name', 'address', 'phone_number', 'logo', 'description',]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'customer', 'text', 'created_at']

# class CartItemSerializer(serializers.ModelSerializer):
#     items = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

#     class Meta:
#         model = CartItem
#         fields = ['id','items', 'quantity']
#         # read_only_fields=['product']
    
#     # def create(self, validated_data):
#     #     product = validated_data.pop('product')  # Remove product from validated_data

#     #     # Get the Listing instance based on the product ID
#     #     listing = Listing.objects.get(product=product)

#     #     # Create the CartItem instance with the remaining validated_data
#     #     cart_item = CartItem.objects.create(product=listing, **validated_data)

#     #     return cart_item

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('id', 'item', 'quantity')

# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = Cart
#         fields = ['user', 'items']

class CartItemCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    def create(self, validated_data):
        cart = self.context['request'].user.cart
        item_id = validated_data['item_id']
        quantity = validated_data['quantity']

        # Check if the cart item already exists
        cart_item = CartItem.objects.filter(cart=cart, item_id=item_id).first()
        if cart_item:
            # Update the quantity of the existing cart item
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item

        # Create a new cart item
        return CartItem.objects.create(cart=cart, item_id=item_id, quantity=quantity)




from django.core.exceptions import ObjectDoesNotExist

class OrderSerializer(serializers.ModelSerializer):
    items = CartItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'seller', 'items', 'total_amount', 'status', 'payment_mode', 'pickup_time', 'delivery_time', 'return_time']
        read_only_fields = ['customer', 'seller']

    def create(self, validated_data):
        created_cart_items = validated_data.pop('items')  # Extract 'items' data from validated_data
        print("created_cart_items",created_cart_items,type(created_cart_items))
        # Create the CartItem instances outside the loop
        # created_cart_items = []
        # for item_data in items_data:
        #     cart_item_serializer = CartItemCreateSerializer(data=item_data, context=self.context)
        #     cart_item_serializer.is_valid(raise_exception=True)
        #     cart_item = cart_item_serializer.save()  # Save the CartItem without 'cart_id'

        #     created_cart_items.append(cart_item)

        # Categorize items by sellers
        seller_items = {}
        for cart_item in created_cart_items:
            print("cart_item",cart_item['item_id'],type(cart_item))
            lis=Listing.objects.filter(id=cart_item['item_id'])
            print("list",lis)
            seller_id = cart_item.item_id.seller_id
            if seller_id not in seller_items:
                seller_items[seller_id] = []
            seller_items[seller_id].append(cart_item)

        orders = []
        for seller_id, items in seller_items.items():
            try:
                # Ensure that each CartItem exists in the database
                for item in items:
                    CartItem.objects.get(pk=item.pk)
            except ObjectDoesNotExist as e:
                raise serializers.ValidationError("Invalid CartItem")

            order_data = {
                'customer': self.context['request'].user,
                'seller': items[0].item.seller,
                'total_amount': sum(item.item.price * item.quantity for item in items),
                'status': 'PENDING',  # Set the initial status as 'PENDING'
                'payment_mode': 'offline',  # Set the default payment mode
            }
            order = Order.objects.create(**order_data)
            orders.append(order)

        # Save the Order objects first before setting the many-to-many relationship
        for order in orders:
            order.save()

        # Set the many-to-many relationship using the 'set()' method
        for order, items in zip(orders, seller_items.values()):
            item_ids = [item.item.id for item in items]  # Get the primary keys (ids) of the Listing objects
            print("Item IDs:", item_ids)
            print("Existing CartItem IDs:", CartItem.objects.values_list('id', flat=True))
            # Before creating the order, ensure all cart items exist in the database
            existing_cart_item_ids = CartItem.objects.values_list('id', flat=True)
            for item_id in item_ids:
                if item_id not in existing_cart_item_ids:
                    # Handle the case when the cart item doesn't exist in the database
                    raise serializers.ValidationError(f"CartItem with ID {item_id} does not exist.")
            order.items.set(item_ids)  # Set the many-to-many relationship with a list of ids

        return orders






# class OrderSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = [ 'customer', 'seller', 'items', 'total_amount', 'status', 'payment_mode', 'pickup_time', 'delivery_time', 'return_time']
#         read_only_fields=['customer', 'seller']
#         def create(self, validated_data):
#             items_data = validated_data.pop('items')
#             order = Order.objects.create(**validated_data)

#             for item_data in items_data:
#                 CartItem.objects.create(order=order, **item_data)

#             return order
        
# class CustomerProfileSerializer(serializers.ModelSerializer):
#     comments = CommentSerializer(many=True, read_only=Tuer)
#     carts = CartSerializer(many=True, read_only=True)
#     orders = OrderSerializer(many=True, read_only=True)
#     ratings=serializers.PrimaryKeyRelatedField(many=True, queryset=Rating.objects.all())

#     class Meta:
#         model = CustomerProfile
#         fields = ['user', 'phone_number', 'address', 'created_at', 'updated_at', 'profile_picture', 'ratings', 'wishlist', 'comments', 'carts', 'orders']

# class ratingSerializer(serializers.ModelSerializer):
#     customer_profile = serializers.SerializerMethodField

#     class Meta:
#         model = Rating
#         fields = ['customerprofile', 'seller', 'products', 'rating']

#     def get_customer_profile(self, obj):
#         customer_profile = obj.customer_profile.all()
#         return CustomerProfileSerializer(customer_profile).data
