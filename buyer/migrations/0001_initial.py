# Generated by Django 5.0.2 on 2024-02-17 17:46

import buyer.models
import django.db.models.deletion
import phonenumber_field.modelfields
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("account", "0001_initial"),
        ("seller", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField(default=1)),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="buyer.cart"
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="seller.listing"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="cart",
            name="items",
            field=models.ManyToManyField(through="buyer.CartItem", to="seller.listing"),
        ),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        default="", max_length=13, region=None
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True,
                        default="/Sameep/media/profile_pic/default_user.jpg",
                        null=True,
                        upload_to=buyer.models.profile_pic_upload_path,
                    ),
                ),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.address",
                    ),
                ),
                ("wishlist", models.ManyToManyField(blank=True, to="seller.listing")),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "products",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="seller.product",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="comments",
                        to="buyer.customerprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "order_id",
                    models.AutoField(editable=False, primary_key=True, serialize=False),
                ),
                ("total_quantity", models.IntegerField(default=1)),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=10
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("IN_TRANSIT", "In Transit"),
                            ("DELIVERED", "Delivered"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "payment_mode",
                    models.CharField(
                        choices=[("online", "Online"), ("offline", "Offline")],
                        default="offline",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("pickup_time", models.DateTimeField(blank=True, null=True)),
                ("delivery_time", models.DateTimeField(blank=True, null=True)),
                ("return_time", models.DateTimeField(blank=True, null=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("items", models.ManyToManyField(to="buyer.cartitem")),
                (
                    "seller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="seller.sellerprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReturnProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "foul_product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="seller.listing"
                    ),
                ),
            ],
        ),
    ]