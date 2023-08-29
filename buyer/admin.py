from django.contrib import admin
from buyer.models import CustomerProfile, Comment, Cart,CartItem, Order
from account.models import User

class CustomerProfileModelAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display=('user','phone_number')
    
    def render_change_form(self, request, context,*args, **kwargs):
        context['adminform'].form.fields["user"].queryset=User.objects.filter(role="buyer")
        # print(context,type(context))
        return super().render_change_form(request, context,*args, **kwargs)
    


class CartItemInline(admin.TabularInline):
    model = CartItem

class CartAdmin(admin.ModelAdmin):
    # list_display = ('id',)
    inlines = [CartItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Filter the queryset to display only cart items related to the user
        if not request.user:
            queryset = queryset.filter(cart__user=request.user)
        return queryset


# Register your models here.
admin.site.register(CustomerProfile,CustomerProfileModelAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem)
admin.site.register(Comment)
admin.site.register(Order)
# admin.site.register(Order)
