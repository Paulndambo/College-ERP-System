from apps.core.models import RolePermission, UserRole
from rest_framework import serializers


from apps.users.models import EmailVerificationOTP, PasswordResetOTP, User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context
from rest_framework.exceptions import ValidationError

from django.core.exceptions import ObjectDoesNotExist

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "gender",
            "phone_number",
            "id_number",
            "passport_number",
            "address",
            "postal_code",
            "city",
            "state",
            "country",
            "date_of_birth",
            "is_verified",
        ]
        read_only_fields = ["id", "role", "is_verified"]

class UserDetailedSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone_number", "role"]
    def get_role(self, obj):
        from apps.core.serializers import UserRoleListSerializer  
        return UserRoleListSerializer(obj.role).data if obj.role else None
class AdminUserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "gender",
            "phone_number",
            "id_number",
            "passport_number",
            "address",
            "postal_code",
            "city",
            "state",
            "country",
            "date_of_birth",
            "is_verified",
        ]
        read_only_fields = ["id"]


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "id_number",
            "passport_number",
            "address",
            "postal_code",
            "state",
            "country",
            "date_of_birth",
            "city",
            "role",
            "password",
        ]

    def validate_email(self, value):
        from apps.core.base_api_error_exceptions import CustomAPIException

        if User.objects.filter(email=value).exists():
            raise CustomAPIException(
                message="This email is already registered.", status_code=400
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            id_number=validated_data.get("id_number", ""),
            passport_number=validated_data.get("passport_number", ""),
            gender=validated_data.get("gender", ""),
            address=validated_data.get("address", ""),
            postal_code=validated_data.get("postal_code", ""),
            city=validated_data.get("city", ""),
            state=validated_data.get("state", ""),
            country=validated_data.get("country", ""),
            date_of_birth=validated_data.get("date_of_birth", ""),
            password=validated_data["password"],
        )
        otp_record = EmailVerificationOTP.objects.create(user=user)
        context = {"name": f"{user.first_name} {user.last_name}", "otp": otp_record.otp}

        message = render_to_string("users/verification_email.html", context)
        send_mail(
            subject="Welcome to our College Erp",
            message="",
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "passport_number",
            "id_number",
            "address",
            "postal_code",
            "city",
            "state",
            "country",
            "date_of_birth",
            "gender",
        ]
        read_only_fields = ["role"]


# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token["user"] = {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "phone_number": user.phone_number,
#             "role": {"id": user.role.id, "name": user.role.name} if user.role else None,
#         }

#         return token

#     def validate(self, attrs):
#         data = super().validate(attrs)
#         user_data = {
#             "id": self.user.id,
#             "username": self.user.username,
#             "email": self.user.email,
#             "first_name": self.user.first_name,
#             "last_name": self.user.last_name,
#             "phone_number": self.user.phone_number,
#             "role": {"id": self.user.role.id, "name": self.user.role.name},
#         }
#         data["user"] = user_data

#         return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        from apps.core.serializers import RolePermissionSerializer

        # Get role with permissions
        role_data = None
        if user.role:
            permissions = RolePermission.objects.filter(role=user.role).select_related("module")
            role_data = {
                "id": user.role.id,
                "name": user.role.name,
                "permissions": RolePermissionSerializer(permissions, many=True).data
            }

        token["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "role": {"id": user.role.id, "name": user.role.name},
        }
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        from apps.core.serializers import RolePermissionSerializer
        role_data = None
        if self.user.role:
            permissions = RolePermission.objects.filter(role=self.user.role).select_related("module")
            role_data = {
                "id": self.user.role.id,
                "name": self.user.role.name,
                "permissions": RolePermissionSerializer(permissions, many=True).data
            }

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "phone_number": self.user.phone_number,
            "role": role_data
        }

        return data
# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):

#         try:
#             user = User.objects.get(email=value)
#         except ObjectDoesNotExist:
#             raise ValidationError("User with provided email not found")

#         reset_otp = PasswordResetOTP.objects.create(user=user)

#         full_name = f"{user.first_name} {user.last_name}"
#         context = {"name": full_name, "otp": reset_otp.otp}

#         message = render_to_string("users/password_reset_email.html", context)
#         send_mail(
#             subject="Your Password Reset Code",
#             message="",
#             html_message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )

#         return value


# class ResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField()
#     new_password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)

#     def validate(self, attrs):
#         email = attrs.get("email")
#         otp = attrs.get("otp")
#         new_password = attrs.get("new_password")
#         confirm_password = attrs.get("confirm_password")

#         if new_password != confirm_password:
#             raise ValidationError("Passwords do not match.")

#         try:
#             user = User.objects.get(email=email)
#             otp_record = PasswordResetOTP.objects.get(user=user, otp=otp, is_used=False)
#         except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
#             raise ValidationError("Invalid OTP or email.")

#         if otp_record.is_expired():
#             raise ValidationError("OTP has expired.")

#         attrs["user"] = user
#         attrs["otp_record"] = otp_record
#         return attrs

#     def save(self, **kwargs):
#         user = self.validated_data["user"]
#         new_password = self.validated_data["new_password"]
#         otp_record = self.validated_data["otp_record"]

#         user.set_password(new_password)
#         user.save()

#         otp_record.is_used = True
#         otp_record.save()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationError("Current password is incorrect")
        return value

    def validate_new_password(self, value):
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
