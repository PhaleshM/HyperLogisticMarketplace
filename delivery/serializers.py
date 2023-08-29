from rest_framework import serializers
from .models import DeliveryAgent, Delivery, PickDrop
from account.serializers import RegionSerializer

class DeliveryAgentSerializer(serializers.ModelSerializer):
    # delivery_region = RegionSerializer(many=True)

    class Meta:
        model = DeliveryAgent
        fields = ("name", 'phone_number', 'aadhar_number', 'adhar_front', 'adhar_back', 'PAN_number', 'PAN_front', 'driving_licence', 'driving_licence_front', 'vehicle_number', 'number_plate')
class DeliverySerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    delivery_agent = serializers.PrimaryKeyRelatedField(queryset=DeliveryAgent.objects.all())

    class Meta:
        model = Delivery
        fields = '__all__'


class PickDropSerializers(serializers.ModelSerializer):
    class Meta:
        model = PickDrop
        fields = '__all__'