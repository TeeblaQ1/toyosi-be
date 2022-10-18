from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions
from authentication.models import User
from orders.models import Order, OrderItem
from orders.serializers import AddToCartSerializer, OrdersSerializer
from shop.models import Product


class OrdersListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrdersSerializer
    queryset = Order.objects.exclude(status='IN_CART')


class OrdersDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrdersSerializer
    queryset = Order.objects.exclude(status='IN_CART')

class CartView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddToCartSerializer

    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            order = Order.objects.filter(user=user, status='IN_CART').first()
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
            order = Order.objects.filter(user=user, status='IN_CART').first()
            if not order:
                # create new order
                order = Order.objects.create(
                    user=user,
                    status='IN_CART',
                    paid=False,
                    meta=""
                )
            # create or update order item
            # check if product already exists in cart
            if order.items.filter(product=product).exists():
                # update order in cart
                order_item = order.items.filter(product=product).first()
                order_item.quantity += quantity
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
                order_in_cart = Order.objects.filter(status='IN_CART', user=user).first()
                order_item = order_in_cart.items.filter(product=product).first()
                order_item.delete()
                message = f'{product.name} deleted from cart'
            else:
                order_in_cart = Order.objects.filter(status='IN_CART', user=user).first()
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




