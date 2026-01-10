from django.contrib.auth.models import Group, Permission
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdminUserRole
from accounts.models import User, UserRole
from accounts import serializers as sz
from accounts.constants import BUSINESS_APPS
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RolePermissionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all Permissson",
        tags=["Only for Super-Admin "],
    )
    def get(self, request):
        if request.user.role != UserRole.SUPER_ADMIN:
            return Response({"detail": "Forbidden"}, status=403)

        response = []

        all_permissions = (
            Permission.objects.select_related("content_type")
            .filter(content_type__app_label__in=BUSINESS_APPS)
            .order_by("content_type__app_label", "content_type__model")
        )

        for group in Group.objects.all():
            group_perm_ids = set(group.permissions.values_list("id", flat=True))

            role_data = {"role": group.name, "apps": {}}

            for perm in all_permissions:
                app = perm.content_type.app_label
                model = perm.content_type.model

                role_data["apps"].setdefault(app, {})
                role_data["apps"][app].setdefault(model, [])

                role_data["apps"][app][model].append(
                    {
                        "id": perm.id,
                        "codename": perm.codename,
                        "name": perm.name,
                        "enabled": perm.id in group_perm_ids,
                    }
                )

            response.append(role_data)

        return Response(response)


class UpdateRolePermissionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update Permissions for user specific group",
        tags=["Only for Super-Admin "],
    )
    def post(self, request):
        if request.user.role != UserRole.SUPER_ADMIN:
            return Response({"detail": "Forbidden"}, status=403)

        role = request.data.get("role")
        permission_ids = request.data.get("permission_ids", [])

        group = Group.objects.get(name=role)
        perms = Permission.objects.filter(id__in=permission_ids)

        group.permissions.set(perms)

        return Response({"status": "updated"})


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    User Management Endpoints (Admin only)
    """

    queryset = User.objects.all()
    serializer_class = sz.UserSerializer
    permission_classes = [IsAdminUserRole]
    http_method_names = ["get", "post", "patch", "delete"]

    @swagger_auto_schema(
        operation_summary="List all users",
        responses={200: sz.UserSerializer(many=True)},
        tags=["Only for Super-Admin "],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a single user",
        responses={200: sz.UserSerializer()},
        tags=["Only for Super-Admin "],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        request_body=sz.UserSerializer,
        responses={
            201: sz.UserSerializer(),
            403: "Only super admin can create new users.",
        },
        tags=["Only for Super-Admin "],
    )
    def create(self, request, *args, **kwargs):
        if request.user.role != UserRole.SUPER_ADMIN:
            return Response(
                {"detail": "Only super admin can create new users."}, status=403
            )
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a user",
        request_body=sz.UserSerializer,
        responses={200: sz.UserSerializer()},
        tags=["Only for Super-Admin "],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        responses={204: "User deleted successfully"},
        tags=["Only for Super-Admin "],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SelfProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get logged-in user profile",
        responses={200: sz.SelfProfileSerializer()},
        tags=["Auth / Account"],
    )
    def get(self, request):
        serializer = sz.SelfProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update logged-in user profile",
        request_body=sz.SelfProfileSerializer,
        responses={200: sz.SelfProfileSerializer()},
        tags=["Auth / Account"],
    )
    def patch(self, request):
        serializer = sz.SelfProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="Register new user",
        operation_description="Create a new user account. Returns JWT tokens.",
        request_body=sz.RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {
                        "message": "Registration successful",
                        "tokens": {"refresh": "string", "access": "string"},
                    }
                },
            ),
            400: "Validation error",
        },
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Registration successful",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Login user using email & password. Returns JWT tokens.",
        request_body=sz.LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "tokens": {"refresh": "string", "access": "string"},
                    }
                },
            ),
            400: "Invalid email or password",
        },
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "message": "Login successful",
                "tokens": {
                    "refresh": serializer.validated_data["refresh"],
                    "access": serializer.validated_data["access"],
                },
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change password",
        request_body=sz.ChangePasswordSerializer,
        responses={200: openapi.Response("Password changed successfully")},
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Request password reset OTP",
        request_body=sz.ForgotPasswordSerializer,
        responses={200: openapi.Response("OTP sent to email")},
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "OTP sent to email"},
            status=status.HTTP_200_OK,
        )


class VerifyOtpView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Verify OTP for password reset",
        request_body=sz.VerifyOtpSerializer,
        responses={200: openapi.Response("OTP verified")},
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "OTP verified"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Reset password",
        request_body=sz.ResetPasswordSerializer,
        responses={200: openapi.Response("Password reset successfully")},
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )


class ResendOtpView(APIView):
    authentication_classes = []

    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Resend OTP for password reset",
        request_body=sz.ResendOtpSerializer,
        responses={200: openapi.Response("OTP sent to email")},
        tags=["Auth / Account"],
    )
    def post(self, request):
        serializer = sz.ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "OTP sent to email"},
            status=status.HTTP_200_OK,
        )


