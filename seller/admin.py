from django.contrib import admin
from account.models import User
from seller.models import Product, SellerProfile, Subscription, Categories, Brand, Listing
# Register your models here.

class SellerProfileModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop_name', 'phone_number', 'get_address')  # Include the 'get_address' method in list_display
    search_fields = ('email', 'shop_name',)
    def render_change_form(self, request, context,*args, **kwargs):
        context['adminform'].form.fields["user"].queryset=User.objects.filter(role="seller")
        # print(context,type(context))
        return super().render_change_form(request, context,*args, **kwargs)

    def get_address(self, obj):
        # Retrieve the address details for the seller profile
        return f"{obj.address.house}, {obj.address.landmark}, {obj.address.region.name}, {obj.address.city.name}"

    get_address.short_description = 'Address'  # Set the column header for the 'get_address' method

class CategoriesModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductModelAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['product_id', 'name', 'brand',
                     'order_count', 'rating', 'is_featured', 'is_available',]


class BrandModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'updated_at']
    prepopulated_fields = {"slug": ("name",)}

class ListingModelAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['product', 'seller','quantity','size','color']


admin.site.register(Product,ProductModelAdmin)
admin.site.register(SellerProfile,SellerProfileModelAdmin)
admin.site.register(Subscription)
admin.site.register(Listing,ListingModelAdmin)
admin.site.register(Categories,CategoriesModelAdmin)
admin.site.register(Brand,BrandModelAdmin)