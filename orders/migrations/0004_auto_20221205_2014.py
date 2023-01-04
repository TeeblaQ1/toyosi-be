# Generated by Django 3.2.16 on 2022-12-05 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_shipping_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='shipping_address',
        ),
        migrations.CreateModel(
            name='OrderDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_address', to='orders.order')),
            ],
        ),
    ]
