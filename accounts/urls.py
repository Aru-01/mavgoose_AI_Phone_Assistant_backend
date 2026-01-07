from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.views import (
    UserViewSet,
    SelfProfileView,
    LoginView,
    RegisterView,
    ChangePasswordView,
    ForgotPasswordView,
    VerifyOtpView,
    ResetPasswordView,
    ResendOtpView,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
urlpatterns = [
    path("me/", SelfProfileView.as_view(), name="self-profile"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("resend-otp/", ResendOtpView.as_view(), name="resend-otp"),
]

urlpatterns += router.urls
