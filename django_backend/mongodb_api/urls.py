from django.urls import path

from .views import (
    mongodb_test,
    mongodb_count,
    detection_collection,
    detection_detail
)


urlpatterns = [

    # --------------------------------------------------------
    # MongoDB connection test
    # --------------------------------------------------------

    path(
        "test/",
        mongodb_test,
        name="mongodb-test"
    ),

    # --------------------------------------------------------
    # MongoDB document count
    # --------------------------------------------------------

    path(
        "count/",
        mongodb_count,
        name="mongodb-count"
    ),

    # --------------------------------------------------------
    # Detection collection
    #
    # GET  -> Get all detections
    # POST -> Create detection
    # --------------------------------------------------------

    path(
        "detections/",
        detection_collection,
        name="detection-collection"
    ),

    # --------------------------------------------------------
    # Single detection
    #
    # GET    -> Get one detection
    # PUT    -> Update detection
    # DELETE -> Delete detection
    # --------------------------------------------------------

    path(
        "detections/<str:detection_id>/",
        detection_detail,
        name="detection-detail"
    ),
]