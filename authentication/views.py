from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.serializers import EmailVerificationSerializer, PasswordChangeSerializer, SavedItemsSerializer, ProfileSerializer, LoginSerializer, LogoutSerializer, RegisterSerializer, RequestPasswordResetEmailSerializer, SetNewPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import Profile, User
from authentication.utils import MailUtil
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, smart_bytes, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from shop.models import Product

class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user = User.objects.get(email=user_data.get("email"))

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        secure_protocol = "https://" if request.is_secure() else "http://"
        absolute_url = secure_protocol + current_site + relative_link + "?token=" + str(token)
        email_body = "Hi " + user.first_name + ",\nPlease use the link below to verify your email \n" + absolute_url
        data = {
            "email_body": email_body,
            "email_subject": "Verify Your Email",
            "to_email": user.email,
        }
        MailUtil.send_email(data)
        return Response({
                'status': 'Success', 
                'message': 'User registration successful', 
                'data': user_data
                }, status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):

    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description="Email verification token", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload.get("user_id"))
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({
                'status': 'Success', 
                'message': 'Email has been successfully verified', 
                'data': {
                    'email': user.email
                }}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({
                'status': 'Failed', 
                'message': 'Activation link has expired, please request for a new link', 
                'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except jwt.exceptions.DecodeError:
            return Response({
                'status': 'Failed', 
                'message': 'Invallid token', 
                'data': {}}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
                'status': 'Success', 
                'message': 'Login successful', 
                'data': serializer.data
                }, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):

    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data={**request.data, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data
        email = serializer_data.get('email', '')
        if User.objects.filter(email=email).exists():
            current_site = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': serializer_data.get('uidb64', ''), 'token': serializer_data.get('token', '')})
            secure_protocol = "https://" if request.is_secure() else "http://"
            absolute_url = secure_protocol + current_site + relative_link
            email_body = "Hi " + serializer_data.get('first_name') + ",\nPlease use the link below to reset your password \n" + absolute_url
            data = {
                "email_body": email_body,
                "email_subject": "Reset Your Password",
                "to_email": serializer_data.get('email'),
            }
            MailUtil.send_email(data)
        return Response({
                'status': 'Success', 
                'message': 'Password Reset Link Sent To Your Mail', 
                'data': serializer.data
                }, status=status.HTTP_200_OK)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({
                    'status': 'Failed', 
                    'message': 'Password reset token no longer valid, please request a new one.', 
                    'data': {}
                    }, status=status.HTTP_401_UNAUTHORIZED)

            return Response({
                'status': 'Success', 
                'message': 'Password Reset Credentials Valid', 
                'data': {
                    'uidb64': uidb64,
                    'token': token
                }
                }, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({
                    'status': 'Failed', 
                    'message': 'Invalid Token, please request a new one.', 
                    'data': {}
                    }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception:
            return Response({
                    'status': 'Failed', 
                    'message': 'Invalid UID or Token, please request a new one.', 
                    'data': {}
                    }, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(generics.GenericAPIView):

    serializer_class = SetNewPasswordSerializer

    def patch(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
                'status': 'Success', 
                'message': 'Password Reset Successful', 
                'data': serializer.data
                }, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):

    serializer_class = LogoutSerializer
    
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ListAddressesAPIView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = ProfileSerializer

    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            address_list = list(Profile.objects.filter(user=user).values('address', 'city', 'state', 'country'))
            address_list = [{
                'first_name': user.first_name,
                'last_name': user.last_name,
                **address
            } for address in address_list]
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
                'status': 'Success', 
                'message': 'List Address View Successful', 
                'data': address_list
                }, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
        data = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=user)
            if Profile.objects.filter(user=user).exists():
                return Response({
                'status': 'Failed', 
                'message': 'Address already exists', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
            profile = Profile.objects.create(
                user=user,
                **data
            )
            profile.save()
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
                'status': 'Success', 
                'message': 'Address Successfully added', 
                'data': user.email
                }, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        data = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=user)
            Profile.objects.filter(user=user).update(
                **data
            )
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
                'status': 'Success', 
                'message': 'Address Successfully updated', 
                'data': user.email
                }, status=status.HTTP_200_OK)
    
    def delete(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            address = Profile.objects.filter(user=user)
            address.delete()
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
                'status': 'Success', 
                'message': 'Address deleted successfully', 
                'data': []
                }, status=status.HTTP_200_OK)


class UpdateProfileAPIView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = ProfileSerializer

    def put(self, request):
        user = request.user
        data = request.data
        try:
            user = User.objects.get(email=user)
            first_name = request.data.pop('first_name', None)
            last_name = request.data.pop('last_name', None)
            user.first_name = first_name if first_name else user.first_name
            user.last_name = last_name if last_name else user.last_name
            user.save()
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            Profile.objects.filter(user=user).update(
                **data
            )
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
                'status': 'Success', 
                'message': 'Address Successfully updated', 
                'data': user.email
                }, status=status.HTTP_200_OK)


class PasswordChangeAPIView(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = PasswordChangeSerializer

    def put(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            old_password = request.data.get('old_password', '')
            new_password = request.data.get('new_password', None)
            new_password_2 = request.data.get('new_password_2', False)
            if new_password != new_password_2:
                raise ValidationError('Passwords mismatch', 400)
            if not user.check_password(old_password):
                raise ValidationError('Current Password Incorrect')
            user.set_password(new_password)
            user.save()
        except:
            return Response({
                'status': 'Failed', 
                'message': 'Unauthorized', 
                'data': []
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
                'status': 'Success', 
                'message': 'Password changed successfully', 
                'data': user.email
                }, status=status.HTTP_200_OK)


class SavedItemsAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SavedItemsSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = request.data.get('product_id', None)
        action = request.data.get('action', None)
        try:
            product = Product.objects.get(id=product_id)
            user = User.objects.get(email=user)
            if action == 'like':
                user.saved_products.add(product)
            if action == 'dislike':
                user.saved_products.remove(product)
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
        phrase = 'added to' if action == 'like' else 'removed from'
        return Response({
                'status': 'Success', 
                'message': f'Product {phrase} saved items', 
                'data': []
                }, status=status.HTTP_200_OK)


    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            saved_items = list(user.saved_products.all().values('id', 'category__id', 'category__name', 'name', 'slug', 'image', 'price'))
            return Response({
                'status': 'Success', 
                'message': 'Saved items loaded successfully', 
                'data': saved_items
                }, status=status.HTTP_200_OK)
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
                user.saved_products.remove(product)
                message = f'{product.name} removed from wishlist'
            else:
                user.saved_products.clear()
            return Response({
                'status': 'Success', 
                'message': message if message else 'Saved items cleared', 
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

class RecentItemsAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(email=user)
            recent_items = list(user.recent_products.all().values('id', 'category__id', 'category__name', 'name', 'slug', 'image', 'price'))
            return Response({
                'status': 'Success', 
                'message': 'Recent items loaded successfully', 
                'data': recent_items
                }, status=status.HTTP_200_OK)
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
                user.recent_products.remove(product)
                message = f'{product.name} removed from recently viewed products'
            else:
                user.recent_products.clear()
            return Response({
                'status': 'Success', 
                'message': message if message else 'Recently Viewed Products Cleared', 
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