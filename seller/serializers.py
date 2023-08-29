from rest_framework import serializers
from account.models import User
from account.serializers import AddressSerializer
from .models import SellerProfile, Subscription
from buyer.models import CustomerProfile
from phonenumbers import PhoneNumberFormat, country_code_for_region, parse as parse_phone_number
from phonenumbers.phonenumberutil import is_valid_number, NumberParseException
from .models import Product, Categories, Brand, Listing
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from account.models import User,Address,City,Region



# class SellerProfileSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source='user.email', read_only=True)

#     class Meta:
#         model = SellerProfile
#         fields = ['email','shop_name','address','phone_number','logo','description','subscription']


# class SellerProfileSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(source='user.email', read_only=True)
#     city = serializers.CharField()
#     rgion = serializers.CharField()
#     house = serializers.CharField()
#     landmark = serializers.CharField()

#     class Meta:
#         model = SellerProfile
#         fields = ['email','shop_name', 'phone_number', 'logo', 'description', 'city', 'region', 'house', 'landmark','subscription']

#     def create(self, validated_data):
#         city_name = validated_data.pop('city')
#         region_name = validated_data.pop('region')
#         house = validated_data.pop('house')
#         landmark = validated_data.pop('landmark')

#         city = get_object_or_404(City, name=city_name)
#         rgion = get_object_or_404(Region, name=region_name)

#         address = Address.objects.create(city=city, region=region, house=house, landmark=landmark)

#         now = timezone.now()
#         validated_data['created_at'] = now  # Set the 'created_at' field value

#         seller_profile = SellerProfile.objects.create(address=address, **validated_data)
#         return seller_profile



class SellerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    categories = serializers.SlugRelatedField(
    slug_field='name',
    queryset=Categories.objects.all(),
    many=True
    )

    def get_address(self, obj):
        address = obj.user.address
        return {
            'house': address.house,
            'landmark': address.landmark,
            # 'pin_code': address.pin_code,
            'city': address.city.name,
            'region': address.region.name,
            # 'pincode': address.region.pincode,
        }

    class Meta:
        model = SellerProfile
        fields = ['email', 'shop_name', 'address', 'phone_number','categories', 'logo', 'description', 'subscription','gst','acc_no','ifsc_no','benifichiery_name']

    def validate_phone_number(self, value):
        """
        Custom validation for phone number field.
        Ensure that the phone number is not already registered and is in the Indian region.
        """
        # Check if the phone number is already registered
        if SellerProfile.objects.filter(phone_number=value).exists() and CustomerProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")

        # Check if the phone number is in the Indian region and is valid
        try:
            parsed_number = parse_phone_number(value, "IN")
            if not is_valid_number(parsed_number):
                raise serializers.ValidationError("The phone number entered is not valid for the Indian region.")
        except NumberParseException:
            raise serializers.ValidationError("The phone number entered is not valid.")

        return value

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        seller_profile = SellerProfile.objects.create(**validated_data)

        categories = Categories.objects.filter(id__in=[category_data['id'] for category_data in categories_data])
        seller_profile.categories.set(categories)

        return seller_profile

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', [])  # Remove categories from validated_data

        # Update fields of the SellerProfile instance
        instance.shop_name = validated_data.get('shop_name', instance.shop_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.description = validated_data.get('description', instance.description)
        instance.gst = validated_data.get('gst', instance.gst)       
        instance.ifsc_no = validated_data.get('ifsc_no', instance.ifsc_no)
        instance.benifichiery_name = validated_data.get('benifichiery_name', instance.benifichiery_name)
        instance.acc_no = validated_data.get('acc_no', instance.acc_no)

        instance.save()

        # Update categories of the SellerProfile instance
        categories = Categories.objects.filter(name__in=categories_data)
        instance.categories.set(categories)

        return instance
    

class ViewSellerProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'address', 'phone_number', 'logo', 'description',]


class CategoriesField(serializers.Field):
    def to_internal_value(self, data):
        try:
            # Try to parse data as a list of integers
            return [int(value) for value in data]
        except (TypeError, ValueError):
            # If parsing fails, assume data is a list of category names
            return data

    def to_representation(self, value):
        return value

class ListingSerializer(serializers.ModelSerializer):
    # product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Add the 'product' field
    seller = serializers.PrimaryKeyRelatedField(read_only=True)  # Make seller field read-only
    # product = serializers.PrimaryKeyRelatedField(read_only=True)  # Add the 'product' field
    class Meta:
        model = Listing
        # fields = '__all__'
        exclude = ('product', )


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Categories.objects.all(),
        many=True
    )
    brand = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Brand.objects.all()
    )
    listing = ListingSerializer(write_only=True, required=True)  # Add the nested serializer for listing

    class Meta:
        model = Product
        # fields = '__all__'
        exclude = ('seller', )

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                categories_names = validated_data.pop('categories')
                categories = []
                for category_name in categories_names:
                    try:
                        category = Categories.objects.get(name=category_name)
                        categories.append(category)
                    except Categories.DoesNotExist:
                        raise ValidationError(f"Invalid category name: {category_name}")

                seller_profile = SellerProfile.objects.get(user=request.user)
                validated_data['seller'] = seller_profile

                # Create the product
                product = Product.objects.create(**validated_data)

                # Set the categories for the product
                product.categories.set(categories)

                listing_data = validated_data.pop('listing')
                listing_data['product'] = product

                # Create the listing for the product and seller
                listing = Listing.objects.create(seller=seller_profile, **listing_data)

                return product

            except SellerProfile.DoesNotExist:
                pass

        return super().create(validated_data)



class ProductUpdateSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Categories.objects.all(),
        many=True
    )
    brand = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Brand.objects.all()
    )
    class Meta:
        model = Product
        fields = ['name', 'description', 'categories', 'brand', 'img1', 'is_featured', 'is_available']


class ListListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'product', 'seller', 'quantity', 'price', 'size', 'color']

class CreateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['product', 'quantity', 'price', 'size', 'color']

class UpdateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['quantity', 'price', 'size', 'color']




# class DiscountedPriceField(serializers.Field):
#     def to_representation(self, value):
#         request = self.context.get('request')
#         if request and hasattr(request.user, 'sellerprofile'):
#             seller_profile = request.user.sellerprofile
#             discounted_price = seller_profile.discount.get(str(value.product_id))
#             if discounted_price is not None:
#                 return discounted_price
#         return None

class ProductListSerializer(serializers.ModelSerializer):
    # images = ImageSerializer(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(), many=True)    
    brand = serializers.SlugRelatedField(slug_field='slug', queryset=Brand.objects.all())
    # discounted_price = DiscountedPriceField(source='*', read_only=True)


    class Meta:
        model = Product
        fields = ['product_id', 'name', 'categories', 'brand',
                  'order_count', 'rating', 'is_featured', 'is_available', 'img1',]

    
class DetailListingSerializer(serializers.ModelSerializer):
    seller = ViewSellerProfileSerializer()  # Include SellerProfileSerializer as a nested serializer

    class Meta:
        model = Listing
        fields = ['id', 'seller', 'quantity', 'price', 'size', 'color']


class ProductDetailSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(), many=True)
    listings = DetailListingSerializer(many=True, read_only=True)  # Custom field for listings

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'categories', 'brand',
                  'order_count', 'rating', 'is_featured', 'is_available',
                  'img1', 'img2', 'img3', 'img4', 'img5', 'listings']

    def get_listings(self, obj):
        listings = Listing.objects.filter(product=obj)[:5]  # Retrieve the associated listings
        return DetailListingSerializer(listings, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['listings'] = self.get_listings(instance)
        return data


# class DiscountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Discount
#         fields = ['code', 'description', 'percentage', 'start_date', 'end_date', 'products']


        # fields = ['product_id', 'name', 'description', 'categories', 'brand',
        #           'order_count', 'rating', 'is_featured', 'is_available',
        #           'img1', 'img2', 'img3', 'img4', 'img5', 'listing']
        # fields = '__all__'


    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         try:
    #             categories_names = validated_data.pop('categories')
    #             categories = []
    #             for category_name in categories_names:
    #                 try:
    #                     category = Categories.objects.get(name=category_name)
    #                     categories.append(category.pk)
    #                 except Categories.DoesNotExist:
    #                     raise ValidationError(f"Invalid category name: {category_name}")

    #             validated_data['categories'] = categories
    #             seller_profile = SellerProfile.objects.get(user=request.user)
    #             validated_data['seller'] = seller_profile

    #             # Create the listing for the product and seller
    #             listing_data = validated_data.pop('listing')
    #             listing = Listing.objects.create(seller=seller_profile, **listing_data)
    #             validated_data['listing'] = listing

    #         except SellerProfile.DoesNotExist:
    #             pass

    #     return super().create(validated_data)

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['plan_name', 'price', 'duration']