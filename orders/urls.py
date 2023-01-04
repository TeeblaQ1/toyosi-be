from django.urls import path
from orders.views import CartView, OrdersListView, OrdersDetailView, OrdersCreateView

urlpatterns = [
    path("cart/", CartView.as_view(), name="orders_in_cart"),
    path("<int:id>/", OrdersDetailView.as_view(), name="orders_detail"),
    path("", OrdersListView.as_view(), name="orders_list"),
    path("pay/", OrdersCreateView.as_view(), name="orders_create"),
]
