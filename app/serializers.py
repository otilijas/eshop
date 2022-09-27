from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, F
from rest_framework import serializers

from app.models import Product, ProductRating, CartItem, Order, OrderItem


class RatingMixin(serializers.Serializer):
    """A mixin for calculating the rating of a product,
    used by different serializers"""
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ["rating"]

    @staticmethod
    def get_rating(obj: Product) -> float:
        if rating_count := obj.ratings.count():
            return round(obj.ratings.aggregate(Sum("rating"))["rating__sum"] / rating_count, 1)
        return 0


class InStockMixin(serializers.Serializer):
    """A mixin for flagging if product is in stock"""
    in_stock = serializers.SerializerMethodField()

    class Meta:
        fields = ["rating"]

    @staticmethod
    def get_in_stock(obj: Product) -> bool:
        return obj.stock > 0


class ProductSerializer(RatingMixin, InStockMixin, serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["id", "name", "image", "price", "stock", "in_stock",
                  "category"] + RatingMixin.Meta.fields + InStockMixin.Meta.fields


class ProductRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductRating
        fields = ["id", "user", "product", "rating", "comment"]
        read_only_fields = ["user"]

    def validate(self, data):
        current_user = self.context["request"].user
        data["user"] = current_user
        if current_user.product_ratings.filter(product=data["product"]).exists():
            raise serializers.ValidationError("Product already has been rated!")
        return data


class ProductInfoSerializer(RatingMixin, InStockMixin, serializers.ModelSerializer):
    ratings = ProductRatingSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "image", "price", "description", "stock", "in_stock",
                  "ratings"] + RatingMixin.Meta.fields + InStockMixin.Meta.fields


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["user", "product", "price", "quantity"]
        read_only_fields = ["price", "user"]

    def to_representation(self, instance: Product) -> dict:
        data = super().to_representation(instance)
        data["product"] = {
            "id": data["product"],
            "name": instance.product.name
        }
        return data

    @transaction.atomic
    def create(self, validated_data):
        cart_item = CartItem.objects.filter(user=self.context["request"].user, product=validated_data["product"],
                                            quantity__gte=1)
        if cart_item.exists():
            validated_data["quantity"] += cart_item[0].quantity
            cart_item.delete()
        validated_data["price"] = validated_data["product"].price
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ["product", "price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "name", "email", "address", "total_amount", "created", "paid", "ordered_items",
                  "order_items"]
        read_only_fields = ["total_amount", "user", "name", "email", "address", "created"]

    def validate(self, data):
        data["user"] = self.context["request"].user
        return data

    @staticmethod
    def get_total_amount(user: User) -> float:
        total_amount = CartItem.objects.filter(user=user).aggregate(
            total_amount=Sum(F("price") * F("quantity")))["total_amount"]
        return total_amount

    @transaction.atomic
    def create(self, validated_data):
        cart_items = CartItem.objects.filter(user=validated_data["user"])
        validated_data["total_amount"] = self.get_total_amount(validated_data["user"])
        validated_data["name"] = validated_data["user"].first_name
        validated_data["email"] = validated_data["user"].email
        order = super().create(validated_data)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.price,
                quantity=item.quantity,
            )
            item.delete()
        return order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email", "address", "orders")
