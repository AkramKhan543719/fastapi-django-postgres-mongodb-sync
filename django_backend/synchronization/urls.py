from django.urls import path

from .views import run_sync


urlpatterns = [

    path(
        "run/",
        run_sync,
        name="run-sync"
    ),

]