from django.urls import path

from .views import (
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    MyProfileUpdateView,
    MyProfileView,
    RegisterUserAPIView,
    ResetPasswordAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserManageView,
    UserRoleCreateAPIView,
    UserUpdateAPIView,
    VerifyEmailOTPView,
)

urlpatterns = [
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("verify-email/", VerifyEmailOTPView.as_view(), name="verify-email"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("user-roles/create/", UserRoleCreateAPIView.as_view(), name="userrole-create"),
    path("profile/", MyProfileView.as_view(), name="my-profile"),
    path("profile/update/", MyProfileUpdateView.as_view(), name="update-my-profile"),
    path("users/<int:pk>/", UserManageView.as_view(), name="manage-user"),
    path("update/<int:pk>/", UserUpdateAPIView.as_view(), name="update-user"),
]
