from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework import permissions, status
from authentication.models import User
from shop.models import Category, Product, ProductImage
from shop.serializers import CategoriesListSerializer, CategoryDetailSerializer, ProductDetailSerializer, ProductsListSerializer
from rest_framework.response import Response

class ProductsListAPIView(ListAPIView):
    
    serializer_class = ProductsListSerializer
    queryset = Product.objects.all()
    permission_classes = (permissions.IsAuthenticated,)



class ProductDetailAPIView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, id):
        user = request.user
        try:
            user = User.objects.get(email=user)
            # add to user's recently viewed items
            product_instance = Product.objects.get(id=id)
            product_instance.user_recent.add(user)
            product = list(Product.objects.filter(id=id).values('name', 'slug', 'image', 'description', 'price', 'category'))[0]

            other_images = list(ProductImage.objects.filter(product=Product.objects.get(id=id)).values('other_image', 'image_description'))
        except Product.DoesNotExist:
            return Response({
                'status': 'Failed', 
                'message': 'Product Not Found', 
                'data': []
                }, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'status': 'Success', 
            'message': 'Product Detail View', 
            'data': {
                **product,
                "extra_images": other_images
            }
            }, status=status.HTTP_200_OK)


class CategoriesListAPIView(ListAPIView):
    
    serializer_class = CategoriesListSerializer
    queryset = Category.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    

class CategoryDetailAPIView(RetrieveAPIView):
    serializer_class = CategoryDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.all()

