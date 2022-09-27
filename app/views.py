from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from app.filters import CategoryFilter
from app.models import CartItem, Order, Product
from app.serializers import CartItemSerializer, OrderSerializer, \
    ProductSerializer, ProductInfoSerializer, ProductRatingSerializer


class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Provides products list and product details with description"""
    queryset = Product.objects.prefetch_related("ratings").all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = CategoryFilter
    search_fields = ["$name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductInfoSerializer
        return ProductSerializer


class ProductRatingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Creates rating for """
    serializer_class = ProductRatingSerializer
    permission_classes = [IsAuthenticated]


class UserOrdersViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """Provides all orders of current user,
     creates order from cart items deleting previous cart items"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.prefetch_related("ordered_items")\
            .select_related("user").filter(user=self.request.user.id).order_by("-created")


class CartItemViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Adds specific item to cart, shows all items in cart"""
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.select_related("product").filter(user=self.request.user.id)
