from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from .views import profile


urlpatterns = [

    # Login
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair"
    ),

    # Refresh token
    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh"
    ),

    # Protected profile
    path(
        "profile/",
        profile,
        name="profile"
    ),
]