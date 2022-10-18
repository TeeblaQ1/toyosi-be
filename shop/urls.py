from django.urls import path
from shop.views import CategoriesListAPIView, CategoryDetailAPIView, ProductsListAPIView, ProductDetailAPIView


urlpatterns = [
    path('products/<int:id>/', ProductDetailAPIView.as_view(), name="product_detail"),
    path('products/', ProductsListAPIView.as_view(), name="products_list"),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name="category_detail"),
    path('categories/', CategoriesListAPIView.as_view(), name="categories_list"),
]
