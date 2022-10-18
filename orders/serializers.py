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