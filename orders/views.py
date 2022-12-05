from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions
from authentication.models import User
from orders.models import Order, OrderItem, OrderDelivery, IN_CART, ORDER_PLACED, ORDER_CANCELED, ORDER_RETURNED, ORDER_DELIVERED, ORDER_DISPATCHED
from orders.serializers import AddToCartSerializer, OrdersDetailSerializer, OrdersSerializer, OrdersDeliverySerializer
from shop.models import Product


class OrdersListView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrdersSerializer
    # queryset = Order.objects.exclude(status=IN_CART)

    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            order = Order.objects.filter(user=user).exclude(status=IN_CART)
            order_data = []
            if order.exists():
                order_data = list(order.values())
            return Response({
                'status': 'Success', 
                'message': f'Order listed succesfully', 
                'data': order_data
                }, status=status.HTTP_200_OK)
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)


class OrdersDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrdersDetailSerializer

    def get(self, request, id):
        user = request.user
        try:
            user = User.objects.get(email=user)
            order = Order.objects.filter(id=id, user=user).first()
            if not order:
                return Response({
                    'status': 'Failed', 
                    'message': f'Order with id {id} not found', 
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)
            order_items = list(OrderItem.objects.filter(order=order).values('product_id', 'product__name', 'price', 'quantity'))
            order_shipping_address = order.shipping_address.all().first()
            return Response({
                'status': 'Success', 
                'message': f'Order in cart loaded', 
                'data': {
                    "order_id": order.id,
                    "status": order.status,
                    "paid": order.paid,
                    "created": order.created,
                    "receipt_number": order.receipt_number,
                    "order_cost": order.get_total_cost(),
                    "billing_address": {
                        "first_name": order.user.first_name,
                        "last_name": order.user.last_name,
                        "email": order.user.email,
                        "phone": order.user.phone,
                        "address": order.user.profile.address,
                        "city": order.user.profile.city,
                        "state": order.user.profile.state,
                        "country": order.user.profile.country
                        },
                    "shipping_address": {
                        "first_name": order_shipping_address.first_name if order_shipping_address else None,
                        "last_name": order_shipping_address.last_name if order_shipping_address else None,
                        "email": order_shipping_address.email if order_shipping_address else None,
                        "phone": order_shipping_address.phone if order_shipping_address else None,
                        "address": order_shipping_address.address if order_shipping_address else None,
                        "city": order_shipping_address.city if order_shipping_address else None,
                        "state": order_shipping_address.state if order_shipping_address else None,
                        "country": order_shipping_address.country if order_shipping_address else None,
                    },
                    "order_items": order_items
                    }
                }, status=status.HTTP_200_OK)
        except:
            import logging
            logging.exception('Error!')
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
class CartView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddToCartSerializer

    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            order = Order.objects.filter(user=user, status=IN_CART).first()
            order_items = []
            if order:
                order_items = list(OrderItem.objects.filter(order=order).values())
            return Response({
                'status': 'Success', 
                'message': f'Order in cart loaded', 
                'data': order_items
                }, status=status.HTTP_200_OK)
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        user = request.user

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        try:
            product = Product.objects.get(id=product_id)
            user = User.objects.get(email=user)
            order = Order.objects.filter(user=user, status=IN_CART).first()
            if not order:
                # create new order
                order = Order.objects.create(
                    user=user,
                    status=IN_CART,
                    paid=False,
                    meta=""
                )
            # create or update order item
            # check if product already exists in cart
            if order.items.filter(product=product).exists():
                # update order in cart
                order_item = order.items.filter(product=product).first()
                order_item.quantity = quantity
                order_item.save()
            else:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )
            return Response({
                'status': 'Success', 
                'message': 'Cart updated successfully', 
                'data': []
                }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                'status': 'Failed', 
                'message': 'Product not found', 
                'data': []
                }, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
    
    def delete(self, request):
        user = request.user
        product_id = self.request.query_params.get("product_id")
        message = None
        try:
            user = User.objects.get(email=user)
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                order_in_cart = Order.objects.filter(status=IN_CART, user=user).first()
                order_item = order_in_cart.items.filter(product=product).first()
                order_item.delete()
                message = f'{product.name} deleted from cart'
            else:
                order_in_cart = Order.objects.filter(status=IN_CART, user=user).first()
                order_in_cart.delete()
            return Response({
                'status': 'Success', 
                'message': message if message else 'Cart cleared successfully', 
                'data': []
                }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                'status': 'Failed', 
                'message': 'Product not found', 
                'data': []
                }, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)


class OrdersCreateView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = OrdersDeliverySerializer

    def post(self, request):
        user = request.user

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = request.data.get('order_id')
        shipping_address = request.data.get('shipping_address')
        try:
            user = User.objects.get(email=user)
            order = Order.objects.filter(id=order_id, user=user, status=IN_CART)
            if not order.exists():
                return Response({
                'status': 'Failed', 
                'message': f'Order with id {order_id} not found', 
                'data': []
                }, status=status.HTTP_404_NOT_FOUND)

            order = Order.objects.filter(id=order_id, user=user, status=IN_CART).first()
            order.status = ORDER_PLACED
            order.save()

            order_delivery = OrderDelivery(
                **{
                    "first_name": shipping_address.get('first_name'),
                    "last_name": shipping_address.get('last_name'),
                    "email": shipping_address.get('email'),
                    "phone": shipping_address.get('phone'),
                    "address": shipping_address.get('address'),
                    "city": shipping_address.get('city'),
                    "state": shipping_address.get('state'),
                    "country": shipping_address.get('country'),
                    "order": order
                }
            )
            order_delivery.save()

            return Response({
                'status': 'Success', 
                'message': 'Order placed successfully', 
                'data': []
                }, status=status.HTTP_200_OK)
        except:
            import logging
            logging.exception('Error!')
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)

