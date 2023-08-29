from django.urls import path, include
from .views import SellerProfileCreateView,SellerProfileUpdateView, SubscriptionListView, SubscriptionDetailView
from .views import ProductListAPIView,CreateProductAPIView,ProductDetailView,ProductUpdateView,ProductDeleteView,CreateListingView,UpdateListingView,ListSellerListingsView,DeleteListingView,SellerProfileListAPI
SellerProfileListAPI
urlpatterns = [
    path('', SellerProfileListAPI.as_view(), name='list-seller-profile'),
    path('seller-profile/', SellerProfileCreateView.as_view(), name='seller-profile-create'),
    path('seller-profile/update/', SellerProfileUpdateView.as_view(), name='seller-profile-update'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', CreateProductAPIView.as_view(), name='product-create'),
    path('products/update/<int:product_id>/', ProductUpdateView.as_view(), name='product-update'),
    path('products/delete/<int:product_id>/', ProductDeleteView.as_view(), name='product-delete'),
    # path('seller-profile/add-product/<int:product_id>/', AddProductToSellerProfile.as_view(), name='add-product-to-seller-profile'),
    path('listings/create/', CreateListingView.as_view(), name='create_listing'),
    path('listings/update/<int:pk>/', UpdateListingView.as_view(), name='update_listing'),
    path('listings/delete/<int:pk>/', DeleteListingView.as_view(), name='delete_listing'),
    path('listings/', ListSellerListingsView.as_view(), name='list_seller_listings'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),

]
