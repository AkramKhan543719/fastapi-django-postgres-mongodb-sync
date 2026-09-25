import hashlib
import json

from datetime import datetime
from typing import Any, Dict, List, Optional

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


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/api/v2/activity-events",

    tags=[
        "V2 Activity Events"
    ]

)


# ============================================================
# V2 ACTIVITY EVENT SCHEMA
# ============================================================

class V2ActivityEvent(BaseModel):

    video_name: str

    person_id: Optional[int] = None

    object_id: Optional[int] = None

    object_type: str

    activity: str

    start_time: str

    end_time: str

    duration_seconds: float

    start_frame: int

    end_frame: int

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    model_name: str

    total_movement_pixels: float = 0.0

    created_at: str


# ============================================================
# V2 REQUEST
# ============================================================

class V2Request(BaseModel):

    video_name: str

    model_name: str

    object_model: str

    fps: float

    total_frames: int

    duration_seconds: float

    summary: Dict[str, Any]

    activity_events: List[
        V2ActivityEvent
    ]

    object_events: List[
        Dict[str, Any]
    ]

    created_at: str


# ============================================================
# V2 RESPONSE
# ============================================================

class V2Response(BaseModel):

    message: str

    event_ids: List[int]

    activity_events: int

    object_events: int

    new_events: int

    duplicate_events: int


# ============================================================
# EVENT HASH CREATION
# ============================================================

def create_event_hash(
    video_name: str,
    event_type: str,
    event_data: Dict[str, Any]
) -> str:

    """
    Creates a deterministic SHA-256 fingerprint
    for one detection/activity event.

    The same video + event type + event data
    always produces the same hash.
    """

    raw = (
        video_name
        + "|"
        + event_type
        + "|"
        + json.dumps(
            event_data,
            sort_keys=True,
            separators=(",", ":"),
            default=str
        )
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# TEST ENDPOINT
# ============================================================

@router.get("/test")
def v2_test():

    return {

        "message":
            "Detection API v2 is working",

        "version":
            "v2",

        "duplicate_protection":
            "enabled"

    }


# ============================================================
# CREATE V2 EVENTS
# ============================================================

@router.post(
    "",
    response_model=V2Response,
    status_code=status.HTTP_201_CREATED
)
def create_v2_events(

    payload: V2Request,

    db: Session = Depends(
        get_db
    )

):

    logger.info(

        "V2 activity data received | "
        "Video: %s",

        payload.video_name

    )

    event_ids = []

    new_events = 0

    duplicate_events = 0

    try:

        # ====================================================
        # ACTIVITY EVENTS
        # ====================================================

        for event in payload.activity_events:

            # ------------------------------------------------
            # Convert Pydantic model to dictionary
            # ------------------------------------------------

            complete_json = event.model_dump()

            # ------------------------------------------------
            # Create deterministic hash
            # ------------------------------------------------

            event_hash = create_event_hash(

                payload.video_name,

                "activity_event",

                complete_json

            )

            # ------------------------------------------------
            # Check whether event already exists
            # ------------------------------------------------

            existing = (

                db.query(
                    DetectionEvent
                )

                .filter(
                    DetectionEvent.event_hash
                    == event_hash
                )

                .first()

            )

            if existing:

                logger.info(

                    "Duplicate activity event skipped | "
                    "Video: %s | "
                    "Existing ID: %s",

                    payload.video_name,

                    existing.id

                )

                event_ids.append(
                    existing.id
                )

                duplicate_events += 1

                continue

            # ------------------------------------------------
            # Create new database record
            # ------------------------------------------------

            db_event = DetectionEvent(

                video_name=
                    payload.video_name,

                event_type=
                    "activity_event",

                class_name=
                    event.object_type,

                confidence=
                    event.confidence,

                timestamp=
                    datetime.utcnow(),

                frame_number=
                    event.start_frame,

                json_data=
                    complete_json,

                event_hash=
                    event_hash

            )

            db.add(
                db_event
            )

            db.flush()

            event_ids.append(
                db_event.id
            )

            new_events += 1

        # ====================================================
        # OBJECT EVENTS
        # ====================================================

        for object_event in payload.object_events:

            # ------------------------------------------------
            # Convert object event to dictionary
            # ------------------------------------------------

            complete_json = dict(
                object_event
            )

            # ------------------------------------------------
            # Extract object information
            # ------------------------------------------------

            object_type = (

                complete_json.get(
                    "object_type",

                    complete_json.get(
                        "class_name",

                        "object"
                    )

                )

            )

            # ------------------------------------------------
            # Extract confidence
            # ------------------------------------------------

            try:

                confidence = float(

                    complete_json.get(
                        "confidence",
                        0.0
                    )

                )

            except (
                TypeError,
                ValueError
            ):

                confidence = 0.0

            # ------------------------------------------------
            # Validate confidence
            # ------------------------------------------------

            if confidence < 0.0:

                confidence = 0.0

            if confidence > 1.0:

                confidence = 1.0

            # ------------------------------------------------
            # Extract frame number
            # ------------------------------------------------

            try:

                frame_number = int(

                    complete_json.get(
                        "frame_number",
                        0
                    )

                )

            except (
                TypeError,
                ValueError
            ):

                frame_number = 0

            # ------------------------------------------------
            # Create deterministic hash
            # ------------------------------------------------

            event_hash = create_event_hash(

                payload.video_name,

                "object_detection_v2",

                complete_json

            )

            # ------------------------------------------------
            # Check duplicate
            # ------------------------------------------------

            existing = (

                db.query(
                    DetectionEvent
                )

                .filter(
                    DetectionEvent.event_hash
                    == event_hash
                )

                .first()

            )

            if existing:

                logger.info(

                    "Duplicate object event skipped | "
                    "Video: %s | "
                    "Existing ID: %s",

                    payload.video_name,

                    existing.id

                )

                event_ids.append(
                    existing.id
                )

                duplicate_events += 1

                continue

            # ------------------------------------------------
            # Create database record
            # ------------------------------------------------

            db_event = DetectionEvent(

                video_name=
                    payload.video_name,

                event_type=
                    "object_detection_v2",

                class_name=
                    object_type,

                confidence=
                    confidence,

                timestamp=
                    datetime.utcnow(),

                frame_number=
                    frame_number,

                json_data=
                    complete_json,

                event_hash=
                    event_hash

            )

            db.add(
                db_event
            )

            db.flush()

            event_ids.append(
                db_event.id
            )

            new_events += 1

        # ====================================================
        # COMMIT
        # ====================================================

        db.commit()

        logger.info(

            "V2 data processed | "
            "Video: %s | "
            "New: %s | "
            "Duplicates: %s",

            payload.video_name,

            new_events,

            duplicate_events

        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "message":
                "V2 activity data processed successfully",

            "event_ids":
                event_ids,

            "activity_events":
                len(
                    payload.activity_events
                ),

            "object_events":
                len(
                    payload.object_events
                ),

            "new_events":
                new_events,

            "duplicate_events":
                duplicate_events

        }

    except Exception as error:

        db.rollback()

        logger.exception(

            "V2 database insertion failed"

        )

        raise HTTPException(

            status_code=
                status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=str(
                error
            )

        )