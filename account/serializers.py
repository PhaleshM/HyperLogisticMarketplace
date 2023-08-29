from rest_framework import serializers
from account.models import User,Address, Region
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import EmailUtil
from seller.models import SellerProfile
from buyer.models import CustomerProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Field for confirming the password during registration
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
  
    class Meta:
        model        = User
        fields       = ['email', 'name', 'password', 'password2', 'tc', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """
        Validate the password and confirm password fields during registration.
        """
        password  = attrs.get('password')
        password2 = attrs.get('password2')
        
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password don't match")
        
        return attrs

    def create(self, validated_data):
        """
        Create a new user based on the validated data.
        """
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    # Field for email during user login
    email = serializers.EmailField(max_length=255)
  
    class Meta:
        model = User
        fields = ['email', 'password']
        # Specifies the model and fields to include in the serializer


# class SellerProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SellerProfile
#         fields = ['shop_name', 'address', 'phone_number', 'logo', 'description', 'products']
#         # Specifies the model and fields to include in the serializer


# class CustomerProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerProfile
#         fields = ['phone_number', 'address', 'profile_picture']
#         # Specifies the model and fields to include in the serializer

class AddressSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='city.name')
    region = serializers.CharField(source='region.name')

    class Meta:
        model = Address
        fields = ['city', 'region', 'house', 'landmark']

class SellerProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'address', 'phone_number', 'logo', 'subscription','gst','acc_no','ifsc_no','bank_name','benifichiery_name']

class CustomerProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'profile_picture']


class UserChangePasswordSerializer(serializers.Serializer):
    # Fields for the new password and confirm password during password change
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']
        # Specifies the fields to include in the serializer

    def validate(self, attrs):
        """
        Validate the new password and confirm password fields during password change.
        """
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password don't match")

        user.set_password(password)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    # Field for the user's email during password reset
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']
        # Specifies the fields to include in the serializer

    def validate(self, attrs):
        """
        Validate the email field during password reset.
        """
        email = attrs.get('email')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Password Reset Token', token)
            link = 'http://localhost:3000/api/user/reset/' + uid + '/' + token
            print('Password Reset Link', link)
            # Send Email
            body = 'Click Following Link to Reset Your Password: ' + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            # EmailUtil.send_email(data) - Uncomment this line to send the email
            return attrs
        else:
            raise serializers.ValidationError('You are not a registered user')


class UserPasswordResetSerializer(serializers.Serializer):
    # Fields for the new password and confirm password during password reset
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']
        # Specifies the fields to include in the serializer

    def validate(self, attrs):
        """
        Validate the new password and confirm password fields during password reset.
        """
        try:
            password  = attrs.get('password')
            password2 = attrs.get('password2')
            uid       = self.context.get('uid')
            token 	  = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password don't match")

            id   = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or has expired')

            user.set_password(password)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not valid or has expired')



# serializer for address 
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'