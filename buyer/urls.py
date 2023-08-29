from django.urls import path, include
from .views import CustomerProfileCreateView,CustomerProfileUpdateView,CartItemCreateView,RemoveFromCartView,CartItemListView, OrderCreateView

urlpatterns = [
    path('customer-profile/', CustomerProfileCreateView.as_view(), name='customer-profile-create'),
    path('customer-profile/update/', CustomerProfileUpdateView.as_view(), name='customer-profile-update'),
    path('cart/add/', CartItemCreateView.as_view(), name='cart-add'),
    # path('cart/update/<int:item__id>/', CartItemUpdateView.as_view(), name='cart-update'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/', CartItemListView.as_view(), name='cart-detail'),
    path('order/create/', OrderCreateView.as_view(), name='create-order'),
]


