from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from database import get_db

from models import DetectionEvent

from logger_config import logger


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(

    prefix="/api/v1/detections",

    tags=["Detections"]
)


# =========================================================
# PYDANTIC SCHEMAS
# =========================================================

class DetectionItem(BaseModel):

    class_name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )


class DetectionRequest(BaseModel):

    video_name: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    timestamp: datetime

    frame_number: int = Field(
        ...,
        ge=0
    )

    detections: List[DetectionItem] = Field(
        ...,
        min_length=1
    )


class DetectionResponse(BaseModel):

    message: str

    event_ids: List[int]


class DetectionEventResponse(BaseModel):

    id: int

    video_name: str

    event_type: str

    class_name: str

    confidence: float

    timestamp: datetime

    frame_number: Optional[int]

    json_data: dict

    created_at: datetime

    sync_status: str

    synced_at: Optional[datetime]

    class Config:

        from_attributes = True


# =========================================================
# TEST ENDPOINT
# =========================================================

@router.get("/test")
def detection_test():

    logger.info(
        "Detection API v1 test endpoint accessed"
    )

    return {

        "message":
            "Detection API v1 is working"
    }


# =========================================================
# CREATE DETECTION EVENTS
# =========================================================

@router.post(
    "",
    response_model=DetectionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_detection_event(

    detection: DetectionRequest,

    db: Session = Depends(get_db)
):

    logger.info(

        "Detection event received | "
        "Video: %s | Frame: %s",

        detection.video_name,

        detection.frame_number
    )

    # =====================================================
    # VALIDATE DETECTION LIST
    # =====================================================

    if not detection.detections:

        logger.warning(
            "Detection event rejected: no detections"
        )

        raise HTTPException(

            status_code=
                status.HTTP_400_BAD_REQUEST,

            detail=
                "Detection list cannot be empty"
        )

    event_ids = []

    try:

        # =================================================
        # CONVERT REQUEST TO JSON
        # =================================================

        complete_json = json.loads(
            detection.json()
        )

        # =================================================
        # PROCESS EACH DETECTION
        # =================================================

        for item in detection.detections:

            # =============================================
            # VALIDATE CLASS NAME
            # =============================================

            if not item.class_name.strip():

                logger.warning(
                    "Detection rejected: empty class name"
                )

                raise HTTPException(

                    status_code=
                        status.HTTP_400_BAD_REQUEST,

                    detail=
                        "class_name cannot be empty"
                )

            # =============================================
            # VALIDATE CONFIDENCE
            # =============================================

            if not 0.0 <= item.confidence <= 1.0:

                logger.warning(
                    "Detection rejected: invalid confidence"
                )

                raise HTTPException(

                    status_code=
                        status.HTTP_400_BAD_REQUEST,

                    detail=
                        "confidence must be between 0 and 1"
                )

            # =============================================
            # CREATE DATABASE EVENT
            # =============================================

            event = DetectionEvent(

                video_name=
                    detection.video_name,

                event_type=
                    detection.event_type,

                class_name=
                    item.class_name,

                confidence=
                    Decimal(
                        str(item.confidence)
                    ),

                timestamp=
                    detection.timestamp,

                frame_number=
                    detection.frame_number,

                json_data=
                    complete_json,

                # New records are waiting
                # for MongoDB synchronization.
                sync_status=
                    "PENDING",

                synced_at=
                    None
            )

            db.add(event)

            db.flush()

            event_ids.append(
                event.id
            )

        # =================================================
        # COMMIT
        # =================================================

        db.commit()

        logger.info(

            "Successfully stored %d "
            "detection events | Video: %s | Frame: %s",

            len(event_ids),

            detection.video_name,

            detection.frame_number
        )

        return {

            "message":
                "Detection events stored successfully",

            "event_ids":
                event_ids
        }

    # =====================================================
    # VALIDATION ERROR
    # =====================================================

    except HTTPException:

        db.rollback()

        raise

    # =====================================================
    # DATABASE / UNEXPECTED ERROR
    # =====================================================

    except Exception as e:

        db.rollback()

        logger.error(

            "Failed to store detection event: %s",

            str(e)
        )

        raise HTTPException(

            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=
                "Failed to store detection event"
        )


# =========================================================
# GET ALL DETECTION EVENTS
# =========================================================

@router.get(
    "",
    response_model=List[DetectionEventResponse]
)
def get_detection_events(

    db: Session = Depends(get_db)
):

    logger.info(
        "Fetching all detection events"
    )

    events = (

        db.query(
            DetectionEvent
        )

        .order_by(
            DetectionEvent.id.desc()
        )

        .all()
    )

    return events


# =========================================================
# GET ONE DETECTION EVENT
# =========================================================

@router.get(
    "/{event_id}",
    response_model=DetectionEventResponse
)
def get_detection_event(

    event_id: int,

    db: Session = Depends(get_db)
):

    logger.info(

        "Fetching detection event ID: %s",

        event_id
    )

    event = (

        db.query(
            DetectionEvent
        )

        .filter(
            DetectionEvent.id == event_id
        )

        .first()
    )

    if event is None:

        logger.warning(

            "Detection event %s not found",

            event_id
        )

        raise HTTPException(

            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Detection event not found"
        )

    return event