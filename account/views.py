from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,AllowAny
from buyer.models import CustomerProfile
from seller.models import SellerProfile
from .serializers import SellerProfileSerializer, CustomerProfileSerializer
from rest_framework_simplejwt.views import TokenRefreshView
# from fcm_django.models import FCMDevice


# Function to generate tokens for a user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class TokenRefreshAPIView(TokenRefreshView):
    pass
        

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        # Create an instance of the UserRegistrationSerializer
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the user and retrieve the saved user instance
        user = serializer.save()

        # Handle FCM token for user's device during registration
        fcm_device_token = request.data.get('fcm_device_token')
        # if fcm_device_token:
        #     FCMDevice.objects.get_or_create(user=user, registration_id=fcm_device_token)
            
        # Generate tokens for the user
        token = get_tokens_for_user(user)
        # Return a response with the token and a success message
        return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        # Create an instance of the UserLoginSerializer
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        # Authenticate the user with the provided email and password
        user = authenticate(email=email, password=password)

        if user is not None:
            # Handle FCM token for user's device during login
            fcm_device_token = request.data.get('fcm_device_token')
            # print("fddsfgfgf",fcm_device_token,"rfgrgregter")
            # if fcm_device_token:
            #     print("fgfsdbdfs")
            #     FCMDevice.objects.get_or_create(user=user, registration_id=fcm_device_token)
            # Generate tokens for the authenticated user
            token = get_tokens_for_user(user)
            role=user.role
            # Return a response with the token and a success message
            return Response({'token': token, 'msg': 'Login Success','role':role}, status=status.HTTP_200_OK)
        else:
            # If authentication fails, return a response with an error message
            return Response({'errors': {'non_field_errors': ['Email or Password is not valid']}},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'seller':
            try:
                seller_profile = SellerProfile.objects.get(user=user)
                serializer = SellerProfileSerializer(seller_profile)
                return Response({"name":user.name,"profile":serializer.data})
            except SellerProfile.DoesNotExist:
                # Return a response indicating that the seller profile was not found
                return Response({"message": "Seller profile not found."}, status=404)
        elif user.role == 'buyer':
            try:
                # Retrieve the buyer profile associated with the user
                buyer_profile = CustomerProfile.objects.get(user=user)
                serializer = CustomerProfileSerializer(buyer_profile)
                return Response({"name":user.name,"profile":serializer.data})
            except CustomerProfile.DoesNotExist:
                # Return a response indicating that the buyer profile was not found
                return Response({"message": "Buyer profile not found."}, status=404)
        else:
            # Return a response indicating that the user role is invalid
            return Response({"message": "Invalid user role."}, status=400)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Create an instance of the UserChangePasswordSerializer
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        # Return a response indicating that the password has been changed successfully
        return Response({'msg': 'Password changed successfully'}, status=status.HTTP_200_OK)


class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        # Create an instance of the SendPasswordResetEmailSerializer
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Return a response indicating that the password reset link has been sent
        return Response({'msg': 'Password reset link sent. Please check your email'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        # Create an instance of the UserPasswordResetSerializer
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        # Return a response indicating that the password has been reset successfully
        return Response({'msg': 'Password reset successfully'}, status=status.HTTP_200_OK)


