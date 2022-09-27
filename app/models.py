import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.html import format_html


class BaseInfo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(BaseInfo):
    CATEGORIES = (
        ("face", "Face Skincare"),
        ("body", "Body Care"),
        ("hair", "Hair Care"),
        ("other", "Other")
    )

    name = models.CharField(max_length=50, db_index=True)
    description = models.TextField(default="")
    image = models.ImageField(upload_to='products/', null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(choices=CATEGORIES, max_length=11, default="other")

    @property
    def thumbnail_preview(self):
        if self.image:
            image_dimensions = 100
            return format_html(
                f"<img src='{self.image.url}' height='{image_dimensions}' width='{image_dimensions}'>")
        return ""

    def __str__(self):
        return self.name


class ProductRating(BaseInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_ratings")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()


class Order(BaseInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    ordered_items = models.ManyToManyField(Product, through="OrderItem")
    name = models.CharField(max_length=50, default="")
    email = models.EmailField(max_length=250, default="")
    address = models.CharField(max_length=550, default="")
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    paid = models.BooleanField(default=False)
    tracking_number = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order({self.id}, {self.total_amount}, {self.created})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ordered item: order ({self.order_id}, product {self.product_id})"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart item: user ({self.user_id}, product {self.product_id})"
