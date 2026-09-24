from rest_framework.decorators import (
    api_view,
    permission_classes
)

from rest_framework.permissions import (
    IsAuthenticated
)

from rest_framework.response import Response


# =========================================================
# PROTECTED USER PROFILE
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):

    user = request.user

    return Response({

        "message":
            "JWT authentication successful",

        "user_id":
            user.id,

        "username":
            user.username,

        "email":
            user.email
    })