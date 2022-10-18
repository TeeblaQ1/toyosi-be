from django.db import models

from authentication.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='toyosi-assets/images/categories/', null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    image = models.ImageField(upload_to='toyosi-assets/images/products/%Y/%m/%d', null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    user_favorites = models.ManyToManyField(User, related_name='saved_products', blank=True)
    user_recent = models.ManyToManyField(User, related_name="recent_products", blank=True)

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='product_image', on_delete=models.CASCADE)
    other_image = models.ImageField(upload_to='toyosi-assets/images/products/%Y/%m/%d', null=True, blank=True)
    image_description = models.CharField(max_length=63, null=True, blank=True)

