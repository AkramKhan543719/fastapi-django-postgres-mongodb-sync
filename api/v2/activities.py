import hashlib
import json

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, status
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
    tags=["V2 Activity Events"]
)


# ============================================================
# ACTIVITY EVENT MODEL
# Matches the actual V2 JSON
# ============================================================

class ActivityEvent(BaseModel):

    video_name: str

    person_id: int

    object_id: Optional[int] = None

    object_type: str = "person"

    activity: str

    start_time: str

    end_time: str

    duration_seconds: float

    start_frame: Optional[int] = None

    end_frame: Optional[int] = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    model_name: Optional[str] = None

    total_movement_pixels: float = 0.0

    created_at: Optional[str] = None


# ============================================================
# OBJECT EVENT MODEL
# Matches the actual V2 JSON
# ============================================================

class ObjectEvent(BaseModel):

    video_name: str

    object_id: Optional[int] = None

    object_type: str

    start_frame: Optional[int] = None

    end_frame: Optional[int] = None

    frame_number: Optional[int] = None

    start_time: Optional[str] = None

    end_time: Optional[str] = None

    duration_seconds: float = 0.0

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    model_name: Optional[str] = None

    created_at: Optional[str] = None


# ============================================================
# V2 REQUEST MODEL
# ============================================================

class V2Request(BaseModel):

    video_name: str

    model_name: Optional[str] = None

    object_model: Optional[str] = None

    fps: float = 0.0

    total_frames: int = 0

    duration_seconds: float = 0.0

    summary: Dict[str, Any] = {}

    activity_events: List[
        ActivityEvent
    ] = []

    object_events: List[
        ObjectEvent
    ] = []

    created_at: Optional[str] = None


# ============================================================
# V2 RESPONSE MODEL
# ============================================================

class V2Response(BaseModel):

    message: str

    video_name: str

    activity_events_received: int

    object_events_received: int

    activity_events_inserted: int

    object_events_inserted: int

    skipped_duplicates: int

    event_ids: List[int]


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

        "format":
            "activity_events + object_events"
    }


# ============================================================
# CREATE ACTIVITY EVENT HASH
# ============================================================

def create_activity_hash(
    event: ActivityEvent
):

    hash_data = {

        "video_name":
            event.video_name,

        "person_id":
            event.person_id,

        "object_id":
            event.object_id,

        "object_type":
            event.object_type,

        "activity":
            event.activity,

        "start_time":
            event.start_time,

        "end_time":
            event.end_time,

        "duration_seconds":
            event.duration_seconds,

        "start_frame":
            event.start_frame,

        "end_frame":
            event.end_frame,

        "confidence":
            event.confidence,

        "model_name":
            event.model_name,

        "total_movement_pixels":
            event.total_movement_pixels
    }

    raw_data = json.dumps(
        hash_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        raw_data.encode("utf-8")
    ).hexdigest()


# ============================================================
# CREATE OBJECT EVENT HASH
# ============================================================

def create_object_hash(
    event: ObjectEvent
):

    hash_data = {

        "video_name":
            event.video_name,

        "object_id":
            event.object_id,

        "object_type":
            event.object_type,

        "start_frame":
            event.start_frame,

        "end_frame":
            event.end_frame,

        "frame_number":
            event.frame_number,

        "start_time":
            event.start_time,

        "end_time":
            event.end_time,

        "duration_seconds":
            event.duration_seconds,

        "confidence":
            event.confidence,

        "model_name":
            event.model_name
    }

    raw_data = json.dumps(
        hash_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        raw_data.encode("utf-8")
    ).hexdigest()


# ============================================================
# POST V2 EVENTS
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
        "V2 data received | Video: %s",
        payload.video_name
    )

    event_ids = []

    activity_events_received = 0

    object_events_received = 0

    activity_events_inserted = 0

    object_events_inserted = 0

    skipped_duplicates = 0

    try:

        # ====================================================
        # ACTIVITY EVENTS
        # ====================================================

        for event in payload.activity_events:

            activity_events_received += 1

            event_hash = create_activity_hash(
                event
            )

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            existing_event = (
                db.query(
                    DetectionEvent
                )
                .filter(
                    DetectionEvent.event_hash
                    == event_hash
                )
                .first()
            )

            if existing_event:

                skipped_duplicates += 1

                event_ids.append(
                    existing_event.id
                )

                logger.info(
                    "Duplicate activity skipped | "
                    "Video=%s | "
                    "Person=%s | "
                    "Activity=%s",
                    event.video_name,
                    event.person_id,
                    event.activity
                )

                continue

            # ------------------------------------------------
            # COMPLETE JSON
            # ------------------------------------------------

            complete_json = {

                "video_name":
                    event.video_name,

                "person_id":
                    event.person_id,

                "object_id":
                    event.object_id,

                "object_type":
                    event.object_type,

                "activity":
                    event.activity,

                "start_time":
                    event.start_time,

                "end_time":
                    event.end_time,

                "duration_seconds":
                    event.duration_seconds,

                "start_frame":
                    event.start_frame,

                "end_frame":
                    event.end_frame,

                "confidence":
                    event.confidence,

                "model_name":
                    event.model_name,

                "total_movement_pixels":
                    event.total_movement_pixels,

                "created_at":
                    event.created_at
            }

            # ------------------------------------------------
            # DATABASE RECORD
            # ------------------------------------------------

            db_event = DetectionEvent(

                video_name =
                    event.video_name,

                event_type =
                    "activity_event",

                class_name =
                    event.activity,

                confidence =
                    event.confidence,

                timestamp =
                    datetime.utcnow(),

                frame_number =
                    event.start_frame,

                json_data =
                    complete_json,

                event_hash =
                    event_hash,

                sync_status =
                    "PENDING"
            )

            db.add(
                db_event
            )

            db.flush()

            event_ids.append(
                db_event.id
            )

            activity_events_inserted += 1

        # ====================================================
        # OBJECT EVENTS
        # ====================================================

        for event in payload.object_events:

            object_events_received += 1

            event_hash = create_object_hash(
                event
            )

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            existing_event = (
                db.query(
                    DetectionEvent
                )
                .filter(
                    DetectionEvent.event_hash
                    == event_hash
                )
                .first()
            )

            if existing_event:

                skipped_duplicates += 1

                event_ids.append(
                    existing_event.id
                )

                logger.info(
                    "Duplicate object skipped | "
                    "Video=%s | "
                    "Object=%s | "
                    "Type=%s",
                    event.video_name,
                    event.object_id,
                    event.object_type
                )

                continue

            # ------------------------------------------------
            # COMPLETE JSON
            # ------------------------------------------------

            complete_json = {

                "video_name":
                    event.video_name,

                "object_id":
                    event.object_id,

                "object_type":
                    event.object_type,

                "start_frame":
                    event.start_frame,

                "end_frame":
                    event.end_frame,

                "frame_number":
                    event.frame_number,

                "start_time":
                    event.start_time,

                "end_time":
                    event.end_time,

                "duration_seconds":
                    event.duration_seconds,

                "confidence":
                    event.confidence,

                "model_name":
                    event.model_name,

                "created_at":
                    event.created_at
            }

            # ------------------------------------------------
            # DATABASE RECORD
            # ------------------------------------------------

            db_event = DetectionEvent(

                video_name =
                    event.video_name,

                event_type =
                    "object_detection_v2",

                class_name =
                    event.object_type,

                confidence =
                    event.confidence,

                timestamp =
                    datetime.utcnow(),

                frame_number =
                    event.frame_number,

                json_data =
                    complete_json,

                event_hash =
                    event_hash,

                sync_status =
                    "PENDING"
            )

            db.add(
                db_event
            )

            db.flush()

            event_ids.append(
                db_event.id
            )

            object_events_inserted += 1

        # ====================================================
        # COMMIT
        # ====================================================

        db.commit()

        logger.info(
            "V2 processing completed | "
            "Video=%s | "
            "Activities inserted=%s | "
            "Objects inserted=%s | "
            "Duplicates=%s",
            payload.video_name,
            activity_events_inserted,
            object_events_inserted,
            skipped_duplicates
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return V2Response(

            message =
                "V2 activity and object data processed successfully",

            video_name =
                payload.video_name,

            activity_events_received =
                activity_events_received,

            object_events_received =
                object_events_received,

            activity_events_inserted =
                activity_events_inserted,

            object_events_inserted =
                object_events_inserted,

            skipped_duplicates =
                skipped_duplicates,

            event_ids =
                event_ids
        )

    except Exception as error:

        db.rollback()

        logger.exception(
            "V2 processing failed | Video=%s",
            payload.video_name
        )

        raise error