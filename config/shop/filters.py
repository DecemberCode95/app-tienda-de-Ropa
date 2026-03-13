import django_filters
from rest_framework import filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    Custom filter for Product queryset.
    Allows filtering by category, price range, and search.
    """
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category'
    )
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )
    in_stock = django_filters.BooleanFilter(
        field_name='stock',
        method='filter_in_stock'
    )
    
    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'price_min', 'price_max', 'in_stock']
