from django.urls import path
from .views import DeliveryAgentOrders, ChooseDeliveryAgent, AssignDeliveryRegions, DeliveryAgentCreateView

urlpatterns = [
    path('delivery-agent-orders/<int:delivery_agent_id>/', DeliveryAgentOrders.as_view(), name='delivery-agent-orders'),
    path('choose-delivery-agent/<int:seller_id>/', ChooseDeliveryAgent.as_view(), name='choose-delivery-agent'),
    path('delivery-agent/<int:delivery_agent_id>/assign-regions/', AssignDeliveryRegions.as_view(), name='assign-delivery-regions'),
    path('create-delivery-agent/', DeliveryAgentCreateView.as_view(), name='create-delivery-agent'),

]
