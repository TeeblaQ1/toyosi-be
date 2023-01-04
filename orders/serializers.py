from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from orders.models import Order

class OrdersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate(self, attrs):
        quantity = attrs.get('quantity')
        if quantity <= 0:
            raise ValidationError('Invalid quantity')
        return super().validate(attrs)

class ShippingAdressObjectSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255, min_length=2)
    last_name = serializers.CharField(max_length=255, min_length=2)
    email = serializers.CharField(max_length=255, min_length=2)
    phone = serializers.CharField(max_length=255, min_length=2)
    address = serializers.CharField(max_length=1024, min_length=2)
    city = serializers.CharField(max_length=255, min_length=2)
    state = serializers.CharField(max_length=255, min_length=2)
    country = serializers.CharField(max_length=255, min_length=2)

class OrdersDeliverySerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    shipping_address = ShippingAdressObjectSerializer()

    def validate(self, attrs):
        return super().validate(attrs)

class OrdersDetailSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate(self, attrs):
        return super().validate(attrs)
