import django_filters
from .models import Product,Categories
import unidecode

class ProductFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name='brand__name',lookup_expr='icontains')
    seller = django_filters.CharFilter(field_name='seller__shop_name',lookup_expr='iexact')
    categories = django_filters.CharFilter(
        field_name='categories__name',
        method='filter_categories'
    )
    region = django_filters.CharFilter(
        field_name='address__region',
        method='filter_categories'
    )
    
    def filter_categories(self, queryset, name, value):
        value = unidecode.unidecode(value)  # Remove non-ASCII characters
        return queryset.filter(categories__name__iexact=value)

    def filter_region(self, queryset, name, value):
        value = unidecode.unidecode(value)  # Remove non-ASCII characters
        return queryset.filter(address__region__contain=value)
    
    class Meta:
        model = Product
        fields = ['brand', 'seller', 'categories','region']
