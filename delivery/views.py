from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DeliveryAgent
from .serializers import DeliveryAgentSerializer, RegionSerializer 
from account.models import Region,User
from buyer.models import Order
from buyer.serializers import OrderSerializer
from seller.models import SellerProfile
from time import timezone



# Create your views here.

# NOTE: All the orders with regions that matches regions of delivery agent will be shown to the delivery agent
# and whatever orders he/she wanna pick can pick and drop


# delivery agent registration
class DeliveryAgentCreateView(CreateAPIView):
    serializer_class = DeliveryAgentSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        user=User.objects.get(email=user)
        # name = self.request.data.get('name')
    #     phone_number = self.request.data.get('phone_number')
    #     adhar_card = self.request.data.get('adhar_number')
    #     pan_card = self.request.data.get('PAN_number')
    #     driving_licence = self.request.data.get('driving_licence')
    #     vehicle_number = self.request.data.get('vehicle_number')
        

        # delivery_agent = DeliveryAgent(
        #     user=user,
        # #     name=name,
        # #     phone_number=phone_number,
        # #     adhar_number=adhar_card,
        # #     PAN_number=pan_card,
        # #     driving_licence=driving_licence,
        # #     vehicle_number=vehicle_number
        # )

        serializer.save(user=user)


# let say there are orders with 3 regions, how to takle this situation?

# delivery status
class OrderPickupView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Set the pickup_time to the current time
        order.pickup_time = timezone.now()
        # Update the status to 'In Transit'
        order.status = Order.IN_TRANSIT
        order.save()

        return Response({"message": "Order picked up successfully"}, status=status.HTTP_200_OK)

class OrderDeliveryView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # make delivery man available again
        # Set the pickup_time to the current time
        order.delivery_time = timezone.now()
        # Set the return_time to one hour past delivery_time
        order.return_time = order.delivery_time + timezone.timedelta(hours=1)

        # Update the status to 'Delivered'
        order.status = Order.DELIVERED
        order.save()
        
        return Response({"message": "Order delivered successfully"}, status=status.HTTP_200_OK)


# class DeliveryAgentViewSet(viewsets.ModelViewSet):
#     queryset = DeliveryAgent.objects.all()
#     serializer_class = DeliveryAgentSerializer

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)

#         # Retrieve the list of delivery regions from the request data
#         delivery_regions_data = request.data.get('delivery_region')

#         # Check if the provided regions exist in the database
#         delivery_regions = []
#         for region_data in delivery_regions_data:
#             region_id = region_data.get('id')
#             try:
# #                 region = Region.objects.get(id=region_id)
#                 delivery_regions.append(region)
#             except Region.DoesNotExist:
#                 return Response(f"Region with ID {region_id} does not exist.", status=status.HTTP_400_BAD_REQUEST)

#         # Update the delivery regions for the delivery agent
#         instance.delivery_region.set(delivery_regions)

#         # Save the updated delivery agent
#         instance.save()

#         return Response(serializer.data)


# assign regions to the delivery agents
class AssignDeliveryRegions(APIView):
    # the admins are allowed to assign multiple regions to the delivery agent
    # only admins can interefere with this field
    
    permission_classes = [IsAuthenticated]

    def post(self, request, delivery_agent_id):
        try:
            delivery_agent = DeliveryAgent.objects.get(pk=delivery_agent_id)
        except DeliveryAgent.DoesNotExist:
            return Response({'message': 'Delivery agent not found'}, status=status.HTTP_404_NOT_FOUND)

        region_ids = request.data.get('regions', [])

        if not isinstance(region_ids, list):
            return Response({'message': 'Invalid data format. Regions must be a list of IDs.'}, status=status.HTTP_400_BAD_REQUEST)

        regions = Region.objects.filter(pk__in=region_ids)

        if not regions.exists():
            return Response({'message': 'No valid regions found'}, status=status.HTTP_400_BAD_REQUEST)

        delivery_agent.delivery_regions.set(regions)
        delivery_agent.save()

        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChooseDeliveryAgent(APIView):
    # using geo location fetch the closest delivery agent to the shop
    # or using the assigned regions to the agents, choose a delivery agent that is available or wait untill one becomes available
    
    def get(self, request, seller_id):
        seller = get_object_or_404(SellerProfile, pk=seller_id)
        seller_region = seller.address.region

        delivery_agents = DeliveryAgent.objects.filter(delivery_regions__in=[seller_region])

        if delivery_agents.exists():
            # You can choose any logic here to select the delivery agent,
            # for example, you can select the first agent in the list
            selected_agent = delivery_agents.first()
            serializer = DeliveryAgentSerializer(selected_agent)
            return Response(serializer.data)
        # make the delivery agent not available
        return Response({'message': 'No available delivery agents for this seller region'})


class returnOrder(APIView):
    def post(self, request, order_id,product_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product's category is returnable
        if order.items.item.product.category.returnable:
            current_time = timezone.now()
            if current_time <= order.return_time:
                # Handle the return process here
                # Update the order status, process the return, etc.
                return Response({"message": "Product returned successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Product cannot be returned now"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Product is not returnable"}, status=status.HTTP_400_BAD_REQUEST)


# till now the functionality part is done,
# where one can create deliveryAgent, assign regions to them, status updation
# delivery app view api will be created now

class DeliveryAgentOrders(APIView):
    def get(self, request, delivery_agent_id):
        delivery_agent = DeliveryAgent.objects.get(pk=delivery_agent_id)
        regions = delivery_agent.delivery_regions.all()
        region_ids = regions.values_list('id', flat=True)
        orders = Order.objects.filter(region__in=region_ids)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
