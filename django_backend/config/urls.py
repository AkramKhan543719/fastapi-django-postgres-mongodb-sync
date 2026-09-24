from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    # Django Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # MongoDB API
    path(
        "api/mongodb/",
        include("mongodb_api.urls")
    ),

    # JWT Authentication
    path(
        "api/auth/",
        include("authentication.urls")
    ),

    # PostgreSQL <-> MongoDB Synchronization
    path(
        "api/sync/",
        include("synchronization.urls")
    ),

]