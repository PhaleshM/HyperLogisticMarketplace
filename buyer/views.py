from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomerProfileSerializer,CartItemSerializer,CartItemCreateSerializer
from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateAPIView,UpdateAPIView,DestroyAPIView,RetrieveAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import CustomerProfile,Cart,CartItem,Order,ReturnProduct
from account.models import User,Address,City,Region
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from rest_framework.exceptions import NotFound
from rest_framework import status
from seller.models import Listing
from django.shortcuts import render
from .serializers import OrderSerializer



# class CustomerProfileCreateView(CreateAPIView):
#     serializer_class = CustomerProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user_email = self.request.user.email
#         user = User.objects.get(email=user_email)
#         serializer.save(user=user)

class CustomerProfileCreateView(CreateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        
        user_email = self.request.user.email
        user = User.objects.get(email=user_email)

        city_name = self.request.data.get('city')
        region_name = self.request.data.get('region')
        house = self.request.data.get('house')
        street = self.request.data.get('street')

        # Get the City instance
        city = get_object_or_404(City, name=city_name)

        # Get or create the Region instance within the selected City
        region = get_object_or_404(Region, name=region_name)

        # Create or update the Address instance
        address = Address.objects.create(city=city, region=region, house=house, street=street)

        # Create the CustomerProfile instance
        customer_profile = CustomerProfile(user=user, phone_number=self.request.data.get('phone_number'),
                                           profile_picture=self.request.data.get('profile_picture'))
        customer_profile.address = address  # Associate the Address instance with the CustomerProfile
        customer_profile.save()
        serializer.instance = customer_profile

class CustomerProfileUpdateView(UpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_email = self.request.user.email
        return get_object_or_404(CustomerProfile, user__email=user_email)

    def perform_update(self, serializer):
        city_name = self.request.data.get('city')
        region_name = self.request.data.get('region')
        house = self.request.data.get('house')
        street = self.request.data.get('street')

        address = serializer.instance.address

        # Update the address fields
        address.city = get_object_or_404(City, name=city_name)
        address.region = get_object_or_404(Region, name=region_name)
        address.house = house
        address.street = street
        address.save()

        serializer.save()


class CustomerProfileDestroyView(DestroyAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CustomerProfile.objects.filter(user=user)

class CartItemListView(ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CartItem.objects.filter(cart=self.request.user.cart)
        
class CartItemCreateView(CreateAPIView):
    serializer_class = CartItemCreateSerializer
    permission_classes = (IsAuthenticated,)

class RemoveFromCartView(DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'item_id'


# class OrderCreateView(APIView):
#     def post(self, request, format=None):
#         user = request.user

#         try:
#             cart = Cart.objects.get(user=user)
#             # cart_items = cart.items.all()
#             cart_items=cart.cartitem_set.all()
#             # Calculate total amount by summing the prices of each listing in the cart
#             # for cart_item in cart_items: 
#             #     print("dffgerg",cart_item.price,type(cart_item))
#             # for cart_item in cart_items: 
#             #     print("dffgerg",cart_item.quantity,type(cart_item))
#             # dffgerg 60.00 <class 'seller.models.Listing'>
#             # dffgerg 453.00 <class 'seller.models.Listing'>
#             # dffgerg 60.00 <class 'buyer.models.CartItem'>
#             # dffgerg 453.00 <class 'buyer.models.CartItem'>


#             total_amount = sum(cart_item.item.price * cart_item.quantity for cart_item in cart_items)

#             # Create the order
#             order = Order.objects.create(
#                 customer=user,
#                 total_amount=total_amount,
#                 status='PENDING',
#                 payment_mode='offline',
#                 pickup_time=None,
#                 delivery_time=None,
#                 return_time=None
#             )
#             order.items.set(cart_items)

#             # Clear the cart items after creating the order
#             cart.items.clear()

#             serializer = OrderSerializer(order)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except Cart.DoesNotExist:
#             return Response({"error": "Cart does not exist for this user."}, status=status.HTTP_404_NOT_FOUND)

from django.core.serializers import serialize

class OrderCreateView(CreateAPIView):
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        cart = request.user.cart
        cart_items = cart.cartitem_set.all()
        print("cart_items",cart_items,type(cart_items))
        for item in cart_items:
            # for x in item:
                print(item)
        # Convert the cart items QuerySet to a list of dictionaries
        cart_items_data = [{"items":[{'item_id': item.item.id, 'quantity': item.quantity} for item in cart_items]}]
        # json = serialize("json", cart_items_data)
        print(cart_items_data)
        # Create the serializer instance with the cart items data
        serializer = self.get_serializer(data=cart_items_data, many=True)        
        serializer.is_valid(raise_exception=True)
        orders = serializer.save()

        # Clear the cart after creating the orders
        cart.cartitem_set.clear()

        return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_201_CREATED)

def create_return_request(request, order_id, product_id):
    user=request.user
    order = get_object_or_404(Order, order_id=order_id)
    product = get_object_or_404(Listing, pk=product_id)

    if order.is_returnable():
        ReturnProduct.objects.create(user=user,order=order, product=product)
        # Return success response
        return Response({'message':'Your request has been accepted'},status=status.HTTP_200_OK)
    else:
        # Return error response indicating that the order is not returnable
        return HttpResponseBadRequest("The order is not returnable.")
    
def index(request):
    return render(request, 'buyer/index.html', {})

def database(request):
    return render(request, 'buyer/database.html', {})