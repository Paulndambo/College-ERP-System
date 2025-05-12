from django.shortcuts import render
from django.shortcuts import render

from apps.users.models import EmailVerificationOTP, User
from services.constants import ALL_ROLES, ALL_STAFF_ROLES
from services.permissions import HasUserRole
from .serializers import AdminUserSerializer, ChangePasswordSerializer, CreateUserSerializer, CustomTokenObtainPairSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserProfileSerializer, UserRoleSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import generics, status
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

class UserLoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    

class UserRoleCreateAPIView(generics.CreateAPIView):
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated] 

class RegisterUserAPIView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]


class VerifyEmailOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
            otp_record = EmailVerificationOTP.objects.get(user=user, otp=otp, is_used=False)

            if otp_record.is_expired():
                return Response({'message': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.save()
            otp_record.is_used = True
            otp_record.save()

            return Response({'message': 'Email verified successfully'})
        except EmailVerificationOTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


   
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    
class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is missing"}, status=400)
            
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
              
                return Response({"message": "Logout successful"}, status=200)
            except TokenError as te:
                return Response({"error": f"Token Error: {str(te)}"}, status=400)
            
        except Exception as e:
            print("Unexpected error:", str(e))
            return Response({"error": f"Unexpected error: {str(e)}"}, status=400)
        
        
class ForgotPasswordAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP sent to your email.Check your email."}, status=status.HTTP_200_OK)
        
        

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()   
        return Response({"message": "Password has been reset successfully."}, status=200)
        
    
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully"}, status=200)
        
        
class MyProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    def get_object(self):
        return self.request.user
    
class MyProfileUpdateView(generics.UpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES


    def get_object(self):
        return self.request.user
    
class UserManageView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES