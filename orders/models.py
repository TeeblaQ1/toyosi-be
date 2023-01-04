from django.db import models
from shop.models import Product
from authentication.models import User, Profile
import uuid
from django.utils.http import int_to_base36


IN_CART = 'IN_CART'
ORDER_PLACED = 'ORDER_PLACED'
ORDER_CANCELED = 'ORDER_CANCELED'
ORDER_RETURNED = 'ORDER_RETURNED'
ORDER_DISPATCHED = 'ORDER_DISPATCHED'
ORDER_DELIVERED = 'ORDER_DELIVERED'

STATUSES = (
    (IN_CART, IN_CART),
    (ORDER_PLACED, ORDER_PLACED),
    (ORDER_CANCELED, ORDER_CANCELED),
    (ORDER_RETURNED, ORDER_RETURNED),
    (ORDER_DISPATCHED, ORDER_DISPATCHED),
    (ORDER_DELIVERED, ORDER_DELIVERED),
)



ID_LENGTH = 12


def id_gen() -> str:
    """Generates random string whose length is of `ID_LENGTH`"""
    return int_to_base36(uuid.uuid4().int)[:ID_LENGTH]

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUSES, max_length=60, default=IN_CART)
    meta = models.JSONField()
    receipt_number = models.CharField(max_length=50, default=id_gen, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        formatted_id = str(self.id).zfill(5)
        return f'#TYS{formatted_id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.order.__str__()} - {self.product.name}'
    
    def get_cost(self):
        return self.price * self.quantity

class OrderDelivery(models.Model):
    order = models.ForeignKey(Order, related_name='shipping_address', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
