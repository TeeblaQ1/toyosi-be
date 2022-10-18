from django.db import models
from shop.models import Product
from authentication.models import User

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

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUSES, max_length=60, default=IN_CART)
    meta = models.JSONField()

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

