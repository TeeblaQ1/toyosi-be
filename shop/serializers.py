from rest_framework import serializers
from shop.models import Category, Product


class ProductsListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'

class CategoriesListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__'


class CategoryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

