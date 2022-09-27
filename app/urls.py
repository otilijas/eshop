from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename="product")
router.register(r'rating', views.ProductRatingViewSet, basename="rating")
router.register(r'orders', views.UserOrdersViewSet, basename="order")
router.register(r'cart', views.CartItemViewSet, basename="cart")

urlpatterns = [
    path('', include(router.urls)),
]
