from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import synchronize_pending_records


# ============================================================
# RUN SYNCHRONIZATION
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def run_sync(request):
    """
    Synchronize all PENDING PostgreSQL detection records
    into MongoDB.
    """

    try:

        result = synchronize_pending_records()

        return Response(
            {
                "message": "PostgreSQL to MongoDB synchronization completed",
                "summary": {
                    "total_pending": result["total_pending"],
                    "synced": result["synced"],
                    "already_synced": result["already_synced"],
                    "failed": result["failed"]
                },
                "results": result["results"]
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:

        return Response(
            {
                "message": "Synchronization failed",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )