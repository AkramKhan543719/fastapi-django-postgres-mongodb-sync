from datetime import datetime

from django.db import connection

from mongodb_api.mongo import detection_events_collection


# ============================================================
# MONGODB INDEX
# ============================================================

def create_mongodb_index():
    """
    Create a unique MongoDB index on postgres_id.

    This prevents duplicate PostgreSQL records from being
    inserted into MongoDB.
    """

    detection_events_collection.create_index(
        "postgres_id",
        unique=True
    )


# ============================================================
# CONVERT POSTGRES ROW TO MONGODB DOCUMENT
# ============================================================

def build_mongodb_document(row):
    """
    Convert a PostgreSQL row into a MongoDB document.

    PostgreSQL column order:

    0  id
    1  video_name
    2  event_type
    3  class_name
    4  confidence
    5  timestamp
    6  frame_number
    7  json_data
    8  created_at
    9  sync_status
    10 synced_at
    """

    return {
        "postgres_id": row[0],
        "video_name": row[1],
        "event_type": row[2],
        "class_name": row[3],
        "confidence": float(row[4]),
        "timestamp": row[5],
        "frame_number": row[6],
        "json_data": row[7],
        "created_at": row[8],
        "synced_at": datetime.utcnow()
    }


# ============================================================
# UPDATE POSTGRESQL SYNC STATUS
# ============================================================

def mark_as_synced(postgres_id, synced_at):
    """
    Mark a PostgreSQL detection record as successfully synced.
    """

    with connection.cursor() as cursor:

        cursor.execute(
            """
            UPDATE detection_events
            SET
                sync_status = %s,
                synced_at = %s
            WHERE id = %s
            """,
            [
                "SYNCED",
                synced_at,
                postgres_id
            ]
        )


# ============================================================
# SYNCHRONIZE ONE RECORD
# ============================================================

def synchronize_detection_event(row):
    """
    Synchronize one PostgreSQL record to MongoDB.
    """

    postgres_id = row[0]

    # --------------------------------------------------------
    # Check whether this PostgreSQL record already exists
    # in MongoDB.
    # --------------------------------------------------------

    existing_document = detection_events_collection.find_one(
        {
            "postgres_id": postgres_id
        }
    )

    if existing_document:

        synced_at = existing_document.get("synced_at")

        if synced_at is None:
            synced_at = datetime.utcnow()

        mark_as_synced(
            postgres_id,
            synced_at
        )

        return {
            "status": "already_synced",
            "postgres_id": postgres_id,
            "message": "Record already exists in MongoDB"
        }

    # --------------------------------------------------------
    # Build MongoDB document
    # --------------------------------------------------------

    mongo_document = build_mongodb_document(row)

    try:

        # ----------------------------------------------------
        # INSERT INTO MONGODB
        # ----------------------------------------------------

        result = detection_events_collection.insert_one(
            mongo_document
        )

        # ----------------------------------------------------
        # ONLY AFTER MONGODB INSERT SUCCEEDS
        # UPDATE POSTGRESQL
        # ----------------------------------------------------

        synced_at = mongo_document["synced_at"]

        mark_as_synced(
            postgres_id,
            synced_at
        )

        return {
            "status": "synced",
            "postgres_id": postgres_id,
            "mongo_id": str(result.inserted_id),
            "message": "Successfully synchronized"
        }

    except Exception as e:

        return {
            "status": "failed",
            "postgres_id": postgres_id,
            "message": str(e)
        }


# ============================================================
# GET ALL PENDING RECORDS
# ============================================================

def get_pending_records():
    """
    Read PENDING detection records directly from PostgreSQL.

    Using a raw cursor avoids Django JSONField attempting to
    deserialize json_data a second time.
    """

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                id,
                video_name,
                event_type,
                class_name,
                confidence,
                timestamp,
                frame_number,
                json_data,
                created_at,
                sync_status,
                synced_at
            FROM detection_events
            WHERE sync_status = %s
            ORDER BY id ASC
            """,
            [
                "PENDING"
            ]
        )

        return cursor.fetchall()


# ============================================================
# SYNCHRONIZE ALL PENDING RECORDS
# ============================================================

def synchronize_pending_records():
    """
    Synchronize all PENDING PostgreSQL records to MongoDB.
    """

    # --------------------------------------------------------
    # Ensure unique MongoDB postgres_id index exists
    # --------------------------------------------------------

    create_mongodb_index()

    # --------------------------------------------------------
    # Get pending PostgreSQL records
    # --------------------------------------------------------

    pending_records = get_pending_records()

    total = len(pending_records)

    synced = 0

    already_synced = 0

    failed = 0

    results = []

    # --------------------------------------------------------
    # Process each record
    # --------------------------------------------------------

    for row in pending_records:

        result = synchronize_detection_event(row)

        results.append(result)

        if result["status"] == "synced":

            synced += 1

        elif result["status"] == "already_synced":

            already_synced += 1

        elif result["status"] == "failed":

            failed += 1

    # --------------------------------------------------------
    # Return summary
    # --------------------------------------------------------

    return {
        "total_pending": total,
        "synced": synced,
        "already_synced": already_synced,
        "failed": failed,
        "results": results
    }