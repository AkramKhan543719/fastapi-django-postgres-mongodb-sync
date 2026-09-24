from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mongo import detection_events_collection


# ============================================================
# HELPER FUNCTION
# ============================================================

def serialize_document(document):
    """
    Convert MongoDB ObjectId into string so that
    the document can be returned as JSON.
    """

    if document is None:
        return None

    document["_id"] = str(document["_id"])

    return document


# ============================================================
# MONGODB CONNECTION TEST
# ============================================================

@api_view(["GET"])
def mongodb_test(request):
    """
    Test MongoDB connection.
    """

    try:
        from .mongo import test_mongodb_connection

        result = test_mongodb_connection()

        if result:
            return Response(
                {
                    "message": "MongoDB connection successful"
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "MongoDB connection failed"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except Exception as e:
        return Response(
            {
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================
# MONGODB COUNT
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mongodb_count(request):
    """
    Return the number of documents in MongoDB.
    """

    try:
        count = detection_events_collection.count_documents({})

        return Response(
            {
                "count": count
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================
# DETECTION COLLECTION
# GET  -> Get all detections
# POST -> Create detection
# ============================================================

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def detection_collection(request):

    # ========================================================
    # GET ALL DETECTIONS
    # ========================================================

    if request.method == "GET":

        try:
            documents = list(
                detection_events_collection.find().sort("_id", -1)
            )

            serialized_documents = [
                serialize_document(document)
                for document in documents
            ]

            return Response(
                {
                    "count": len(serialized_documents),
                    "detections": serialized_documents
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========================================================
    # POST / CREATE DETECTION
    # ========================================================

    if request.method == "POST":

        data = request.data

        required_fields = [
            "postgres_id",
            "video_name",
            "event_type",
            "class_name",
            "confidence",
            "timestamp",
            "frame_number",
            "json_data",
            "created_at",
            "synced_at"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing_fields:

            return Response(
                {
                    "error": "Missing required fields",
                    "missing_fields": missing_fields
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Check whether postgres_id already exists
        # ----------------------------------------------------

        existing_document = detection_events_collection.find_one(
            {
                "postgres_id": data["postgres_id"]
            }
        )

        if existing_document:

            return Response(
                {
                    "error": "Detection already exists",
                    "postgres_id": data["postgres_id"]
                },
                status=status.HTTP_409_CONFLICT
            )

        # ----------------------------------------------------
        # Create MongoDB document
        # ----------------------------------------------------

        document = {
            "postgres_id": data["postgres_id"],
            "video_name": data["video_name"],
            "event_type": data["event_type"],
            "class_name": data["class_name"],
            "confidence": data["confidence"],
            "timestamp": data["timestamp"],
            "frame_number": data["frame_number"],
            "json_data": data["json_data"],
            "created_at": data["created_at"],
            "synced_at": data["synced_at"]
        }

        try:

            result = detection_events_collection.insert_one(
                document
            )

            created_document = (
                detection_events_collection.find_one(
                    {
                        "_id": result.inserted_id
                    }
                )
            )

            return Response(
                serialize_document(created_document),
                status=status.HTTP_201_CREATED
            )

        except DuplicateKeyError:

            return Response(
                {
                    "error": "Detection with this postgres_id already exists",
                    "postgres_id": data["postgres_id"]
                },
                status=status.HTTP_409_CONFLICT
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# SINGLE DETECTION
#
# GET    -> Get one detection
# PUT    -> Update detection
# DELETE -> Delete detection
# ============================================================

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def detection_detail(request, detection_id):

    # ========================================================
    # Validate MongoDB ObjectId
    # ========================================================

    try:

        object_id = ObjectId(detection_id)

    except Exception:

        return Response(
            {
                "error": "Invalid MongoDB ID"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ========================================================
    # Find document
    # ========================================================

    try:

        document = detection_events_collection.find_one(
            {
                "_id": object_id
            }
        )

    except Exception as e:

        return Response(
            {
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if not document:

        return Response(
            {
                "error": "Detection not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # ========================================================
    # GET SINGLE DETECTION
    # ========================================================

    if request.method == "GET":

        return Response(
            serialize_document(document),
            status=status.HTTP_200_OK
        )

    # ========================================================
    # UPDATE DETECTION
    # ========================================================

    if request.method == "PUT":

        data = request.data

        allowed_fields = [
            "postgres_id",
            "video_name",
            "event_type",
            "class_name",
            "confidence",
            "timestamp",
            "frame_number",
            "json_data",
            "created_at",
            "synced_at"
        ]

        update_data = {
            field: data[field]
            for field in allowed_fields
            if field in data
        }

        if not update_data:

            return Response(
                {
                    "error": "No valid fields provided for update"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # If postgres_id is being changed, make sure it isn't
        # already used by another document.
        # ----------------------------------------------------

        if "postgres_id" in update_data:

            duplicate = detection_events_collection.find_one(
                {
                    "postgres_id": update_data["postgres_id"],
                    "_id": {
                        "$ne": object_id
                    }
                }
            )

            if duplicate:

                return Response(
                    {
                        "error": "Another detection already uses this postgres_id"
                    },
                    status=status.HTTP_409_CONFLICT
                )

        try:

            detection_events_collection.update_one(
                {
                    "_id": object_id
                },
                {
                    "$set": update_data
                }
            )

            updated_document = (
                detection_events_collection.find_one(
                    {
                        "_id": object_id
                    }
                )
            )

            return Response(
                serialize_document(updated_document),
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ========================================================
    # DELETE DETECTION
    # ========================================================

    if request.method == "DELETE":

        try:

            result = detection_events_collection.delete_one(
                {
                    "_id": object_id
                }
            )

            if result.deleted_count == 0:

                return Response(
                    {
                        "error": "Detection not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {
                    "message": "Detection deleted successfully",
                    "mongo_id": detection_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )