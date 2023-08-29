from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from account.models import User,Address,City,Region
from .models import Product,Listing,SellerProfile,Product,Categories, Subscription
from django.core.exceptions import PermissionDenied
from .serializers import ProductSerializer,ProductListSerializer,ProductDetailSerializer,ProductUpdateSerializer,SellerProfileSerializer,ListListingSerializer,CreateListingSerializer,UpdateListingSerializer,ViewSellerProfileSerializer, SubscriptionSerializer
from .filters import ProductFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from geopy.distance import distance
from django.shortcuts import get_object_or_404


# class SellerProfileCreateView(CreateAPIView):
#     serializer_class = SellerProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user_email = self.request.user.email
#         user = User.objects.get(email=user_email)

#         city_name = self.request.data.get('city')
#         region_name = self.request.data.get('region')
#         house = self.request.data.get('house')
#         landmark = self.request.data.get('landmark')

#         # Get the City instance
#         city = get_object_or_404(City, name=city_name)

#         # Get or create the Region instance within the selected City
#         rgion, _ = Region.objects.get_or_create(city=city, name=region_name)

#         # Create or update the Address instance
#         address, _ = Address.objects.update_or_create(city=city, region=region, defaults={'house': house, 'landmark': landmark})

#         try:
#             # Attempt to retrieve the existing SellerProfile instance for the user
#             seller_profile = SellerProfile.objects.get(user=user)

#             # Update the existing SellerProfile with the new data
#             seller_profile.shop_name = self.request.data.get('shop_name')
#             seller_profile.phone_number = self.request.data.get('phone_number')
#             seller_profile.logo = self.request.data.get('logo')
#             seller_profile.description = self.request.data.get('description')
#             seller_profile.address = address
#             seller_profile.save()

#             serializer.instance = seller_profile  # Set the serializer's instance for response serialization

#         except SellerProfile.DoesNotExist:
#             # If the SellerProfile doesn't exist, create a new one
#             seller_profile = SellerProfile(user=user, shop_name=self.request.data.get('shop_name'),
#                                            phone_number=self.request.data.get('phone_number'),
#                                            logo=self.request.data.get('logo'),
#                                            description=self.request.data.get('description'),
#                                            address=address)
#             seller_profile.save()
#             serializer.instance = seller_profile  # Set the serializer's instance for response serialization

class SellerProfileCreateView(CreateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        city_name = self.request.data.get('city')
        region_name = self.request.data.get('region')
        house = self.request.data.get('house')
        landmark = self.request.data.get('landmark')
        shop_name= self.request.data.get('shop_name')
        phone_number= self.request.data.get('phone_number', '')
        logo= self.request.data.get('logo', '')
        description= self.request.data.get('description', '')
        gst= self.request.data.get('gst', '')
        acc_no= self.request.data.get('acc_no', '')
        ifsc_no= self.request.data.get('ifsc_no', '')
        benifichiery_name= self.request.data.get('benifichiery_name', '')

        city = get_object_or_404(City, name=city_name)
        region = get_object_or_404(Region, name=region_name)

        address = Address.objects.create(city=city, region=region, house=house, landmark=landmark)

        seller_profile = SellerProfile(user=user,
                                       address=address,
                                       shop_name=shop_name,
                                       phone_number=phone_number,
                                       logo=logo,
                                       description=description,
                                       gst=gst,
                                       acc_no=acc_no,
                                       ifsc_no=ifsc_no,
                                       benifichiery_name=benifichiery_name
                                       )
        seller_profile.save()

        categories_data = serializer.validated_data.get("categories", [])
        categories = Categories.objects.filter(name__in=categories_data)
        seller_profile.categories.set(categories)

class SellerProfileListAPI(ListAPIView):
    serializer_class = ViewSellerProfileSerializer

    def get_queryset(self):
        queryset = SellerProfile.objects.all()
        region = self.request.query_params.get('region', None)
        category = self.request.query_params.get('category', None)

        if region:
            queryset = queryset.filter(address__region__name__contains=region)
        if category:
            queryset = queryset.filter(categories__name__contains=category)

        return queryset


class SellerProfileUpdateView(UpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_email = self.request.user.email
        return get_object_or_404(SellerProfile, user__email=user_email)

    def perform_update(self, serializer):
        city_name = self.request.data.get('city')
        region_name = self.request.data.get('region')
        house = self.request.data.get('house')
        landmark = self.request.data.get('landmark')


        address = serializer.instance.address

        # Update the address fields
        address.city = get_object_or_404(City, name=city_name)
        address.region = get_object_or_404(Region, name=region_name)
        address.house = house
        address.landmark = landmark
        address.save()

        # Update the seller profile instance
        instance = serializer.instance
        instance.address = address
        # instance.save()

        # Set categories using the set() method
        categories_data = serializer.validated_data.get("categories", [])
        categories = Categories.objects.filter(name__in=categories_data)
        instance.categories.set(categories)

        serializer.save()


class ProductListAPIView(ListAPIView):
    queryset         = Product.objects.filter(is_available=True)  # Filter products by availability
    serializer_class = ProductListSerializer
    filterset_class  = ProductFilter  # Specify the filter set class for additional filtering options
    filter_backends  = [DjangoFilterBackend, SearchFilter]  # Enable both Django filter backend and search filtering
    search_fields    = ['name']  # Specify the fields to search for product names

class ProductDetailView(RetrieveAPIView):
    queryset         = Product.objects.filter(is_available=True)  # Filter products by availability
    serializer_class = ProductDetailSerializer
    lookup_field     = 'product_id'  # Specify the lookup field to retrieve products by their product_id


# class CreateProductAPIView(CreateAPIView):
#     serializer_class = ProductSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         if user.role == 'seller':
#             serializer.save(seller=user.sellerprofile)
#         else:
#             serializer.save(seller=None)


# class CreateProductAPIView(CreateAPIView):
#     serializer_class = ProductSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         if user.is_authenticated and hasattr(user, 'sellerprofile') and user.sellerprofile:
#             product = serializer.save(seller=user.sellerprofile)  # Create the product and associate it with the seller

#             # Create the listing for the product
#             listing = Listing.objects.create(product_id=product, seller=user.sellerprofile)
#             listing_data = ListingSerializer(listing).data  # Serialize the created listing data

#             # Prepare the response data
#             response_data = {
#                 'product': serializer.data,
#                 'listing': listing_data
#             }

#             return Response(response_data, status=status.HTTP_201_CREATED)

#         else:
#             raise PermissionDenied("You must be a logged-in seller to add products.")

class CreateProductAPIView(CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        # print(user)
        if user.is_authenticated:
            seller_profile = user.sellerprofile
            if seller_profile:
                product = serializer.save(seller=seller_profile)
            else:
                raise PermissionDenied("You must have a seller profile to add products.")
        else:
            raise PermissionDenied("You must be logged in.")
        
        
class ProductUpdateView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'product_id'

    def put(self, request, *args, **kwargs):
        product = self.get_object()

        # Check if the user is the seller who created the product or an admin
        if not (request.user.is_staff or product.seller == request.user.sellerprofile):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return self.update(request, *args, **kwargs)


class ProductDeleteView(DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'product_id'

    def delete(self, request, *args, **kwargs):
        product = self.get_object()

        # Check if the user is the seller who created the product or an admin
        if not (request.user.is_staff or product.seller == request.user.sellerprofile):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return self.destroy(request, *args, **kwargs)

# class AddProductToSellerProfile(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, product_id, format=None):
#         try:
#             product = Product.objects.get(pk=product_id)
#             seller_profile = request.user.sellerprofile
#             seller_profile.products.add(product)
#             return Response("Product is Added",status=201)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=404)
        

class CreateListingView(CreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = CreateListingSerializer

    def perform_create(self, serializer):
        # Set the logged-in seller as the seller in the listing
        # print(self.request.user.sellerprofile)
        serializer.save(seller=self.request.user.sellerprofile)

class UpdateListingView(UpdateAPIView):
    queryset = Listing.objects.all()
    serializer_class = UpdateListingSerializer

    def perform_update(self, serializer):
        # Set the logged-in seller as the seller in the listing
        serializer.save(seller=self.request.user.sellerprofile)


class DeleteListingView(DestroyAPIView):
    queryset = Listing.objects.all()
    # serializer_class = ListListingSerializer

    def perform_destroy(self, instance):
        # Check if the logged-in seller is the owner of the listing
        if instance.seller != self.request.user.sellerprofile:
            raise PermissionDenied("You do not have permission to delete this listing.")
        instance.delete()


class ListSellerListingsView(generics.ListAPIView):
    serializer_class = ListListingSerializer

    def get_queryset(self):
        queryset = Listing.objects.all()
        product_id = self.request.query_params.get('product', None)
        seller = self.request.query_params.get('seller', None)

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if seller:
            queryset = queryset.filter(seller=seller)

        return queryset
    

class SubscriptionListView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminUser]

class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminUser]
