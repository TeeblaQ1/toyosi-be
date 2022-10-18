from django.urls import path
from orders.views import CartView, OrdersListView, OrdersDetailView

urlpatterns = [
    path("cart/", CartView.as_view(), name="orders_in_cart"),
    path("<int:pk>/", OrdersDetailView.as_view(), name="orders_detail"),
    path("", OrdersListView.as_view(), name="orders_list"),
]
