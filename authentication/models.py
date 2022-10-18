from email.policy import default
from django.db import models

# Create your models here.
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from authentication.utils import AuthUtil
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, phone, username=None, password=None):
        
        if email is None:
            raise TypeError('Email is required')
        if first_name is None:
            raise TypeError('Firstname is required')
        if last_name is None:
            raise TypeError('Lastname is required')
        if phone is None:
            raise TypeError('Phone number is required')
        username = AuthUtil.get_username(email)
        
        user = self.model(username=username, email=self.normalize_email(email), first_name=first_name, last_name=last_name, phone=phone)
        user.set_password(password)
        user.save()

        return user
    
    def create_superuser(self, email, first_name, last_name, phone, username=None, password=None):
        
        if password is None:
            raise TypeError('Password is required for superuser')
        
        user = self.create_user(email, first_name, last_name, phone, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=16)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def tokens(self):
        tokens = RefreshToken.for_user(self)
        return {
            'refresh': str(tokens),
            'access_token': str(tokens.access_token)
        }


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Profile for user {self.user.email}'

