from django.contrib import admin
from django.urls import path, include

# from debug_toolbar.toolbar import debug_toolbar_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AI Phone Assistant",
        default_version="v1",
        description="""The AI Phone Assistant is a smart, automated system designed to answer customer
                calls for UBreakiFix stores during off-hours or when staff availability is limited.
                The system uses the client’s existing phone scripts and repair price sheets to
                provide accurate, friendly, and professional responses.
                The assistant can handle inquiries about repair costs for cell phones, tablets, game
                consoles, and computer software issues. For complex problems that require
                technician intervention, the AI can perform a warm transfer to live staff.""",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ubreakfix@support.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.urls")),
    path("api/v1/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
# + debug_toolbar_urls()
