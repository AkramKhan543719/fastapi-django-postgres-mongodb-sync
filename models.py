from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    JSON
)

from datetime import datetime

from database import Base


class DetectionEvent(Base):

    __tablename__ = "detection_events"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================================
    # VIDEO INFORMATION
    # =========================================================

    video_name = Column(
        String(255),
        nullable=False,
        index=True
    )

    # =========================================================
    # EVENT INFORMATION
    # =========================================================

    event_type = Column(
        String(100),
        nullable=False
    )

    # =========================================================
    # DETECTION INFORMATION
    # =========================================================

    class_name = Column(
        String(100),
        nullable=False,
        index=True
    )

    confidence = Column(
        Numeric(5, 4),
        nullable=False
    )

    # =========================================================
    # FRAME / TIMESTAMP INFORMATION
    # =========================================================

    timestamp = Column(
        DateTime,
        nullable=False
    )

    frame_number = Column(
        Integer,
        nullable=True
    )

    # =========================================================
    # ORIGINAL JSON DATA
    # =========================================================

    json_data = Column(
        JSON,
        nullable=False
    )

    # =========================================================
    # RECORD CREATION TIME
    # =========================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # =========================================================
    # MONGODB SYNCHRONIZATION STATUS
    # =========================================================

    sync_status = Column(
        String(20),
        default="PENDING",
        nullable=False,
        index=True
    )

    # =========================================================
    # SUCCESSFUL MONGODB SYNC TIME
    # =========================================================

    synced_at = Column(
        DateTime,
        nullable=True
    )

    # =========================================================
    # V2 DUPLICATE PROTECTION
    # =========================================================

    event_hash = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )