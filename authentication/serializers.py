from urllib import request
from rest_framework import serializers
from authentication.models import Profile, User
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from authentication.utils import MailUtil

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password']
    
    def validate(self, attrs):
        return super().validate(attrs)
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RequestVerificationLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=6)

    class Meta:
        fields = ['email',]

    def validate(self, attrs):
            
        return super().validate(attrs)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=8)
    password = serializers.CharField(max_length=64, min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=255, min_length=8, read_only=True)
    last_name = serializers.CharField(max_length=255, min_length=8, read_only=True)
    phone = serializers.CharField(max_length=255, min_length=8, read_only=True)
    tokens = serializers.JSONField(read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Username/Password Mismatch')

        if not user.is_active:
            raise AuthenticationFailed('Account disabled, please contact admin')
        
        if not user.is_verified:
            raise AuthenticationFailed('Email has not yet been verified, please verify your email in order to login')
        
        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'tokens': user.tokens()
        }


class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=6)
    first_name = serializers.CharField(max_length=255, min_length=8, read_only=True)
    uidb64 = serializers.CharField(max_length=255, min_length=1, read_only=True)
    token = serializers.CharField(max_length=555, min_length=2, read_only=True)

    class Meta:
        fields = ['email', 'first_name', 'uidb64', 'token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            return {
                'email': user.email,
                'first_name': user.first_name,
                'uidb64': uidb64,
                'token': token
            }
            
        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=64, min_length=6, write_only=True)
    uidb64 = serializers.CharField(max_length=255, min_length=1, write_only=True)
    token = serializers.CharField(max_length=555, min_length=2, write_only=True)

    class Meta:
        fields = ['password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            uidb64 = attrs.get('uidb64')
            token = attrs.get('token')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Reset token link no longer valid', 401)
            user.set_password(password)
            user.save()

            return user 
            
        except Exception as e:
            raise AuthenticationFailed('Invalid UID or Token', 401)


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class ProfileSerializer(serializers.ModelSerializer):
    # first_name = serializers.CharField(max_length=255, min_length=8, write_only=True)
    # last_name = serializers.CharField(max_length=255, min_length=8, write_only=True)

    class Meta:
        model = Profile
        fields = ['state', 'country', 'city', 'address']
    
    def validate(self, attrs):
        return super().validate(attrs)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=64, min_length=6, write_only=True)
    new_password = serializers.CharField(max_length=64, min_length=6, write_only=True)
    new_password_2 = serializers.CharField(max_length=64, min_length=6, write_only=True)

    def validate(self, attrs):
        return super().validate(attrs)


class SavedItemsSerializer(serializers.Serializer):
    choices = ['like', 'dislike']
    action = serializers.ChoiceField(choices=choices)
    product_id = serializers.IntegerField()

    def validate(self, attrs):
        return super().validate(attrs)