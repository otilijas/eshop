from django.contrib import admin
from django.db.models import Sum

from app.models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "thumbnail_preview", "price", "stock", "category", "rating")
    search_fields = ("name", "category", "price")
    list_filter = ("category",)
    exclude = ("created", "updated")

    @staticmethod
    def rating(obj):
        if rating_count := obj.ratings.count():
            return round(obj.ratings.aggregate(Sum("rating"))["rating__sum"] / rating_count, 1)
        return 0


class ProductsInline(admin.TabularInline):
    model = Order.ordered_items.through
    can_delete = False
    exclude = ("created",)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "created", "paid", "tracking_number")
    search_fields = ("user", "created_at")
    readonly_fields = ("id", "created", "user", "email", "name", "address", "tracking_number", "total_amount")
    list_filter = ("total_amount", "created", "paid")
    inlines = [
        ProductsInline,
    ]
    exclude = ("updated", "ordered_items")
