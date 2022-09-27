from django_filters import rest_framework as filters

from app.models import Product


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["category"]
