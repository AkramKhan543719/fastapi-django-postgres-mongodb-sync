import hashlib
import json

from sqlalchemy import text

from database import engine


# ============================================================
# CREATE HASH
# ============================================================

def create_hash(
    video_name,
    event_type,
    event_data
):

    raw = (

        str(video_name)
        + "|"
        + str(event_type)
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
# MAIN
# ============================================================

def populate_event_hashes():

    print()
    print("=" * 70)
    print("POPULATING EVENT HASHES")
    print("=" * 70)

    with engine.begin() as connection:

        # ----------------------------------------------------
        # Get all existing records
        # ----------------------------------------------------

        result = connection.execute(

            text(
                """
                SELECT
                    id,
                    video_name,
                    event_type,
                    json_data
                FROM detection_events
                WHERE event_hash IS NULL
                ORDER BY id
                """
            )

        )

        records = result.fetchall()

        print(
            f"Records requiring hashes: {len(records)}"
        )

        processed = 0

        for record in records:

            record_id = record[0]

            video_name = record[1]

            event_type = record[2]

            json_data = record[3]

            # ------------------------------------------------
            # Convert JSON safely
            # ------------------------------------------------

            if isinstance(
                json_data,
                dict
            ):

                event_data = json_data

            else:

                try:

                    event_data = json.loads(
                        json_data
                    )

                except Exception:

                    event_data = {
                        "raw_data":
                            str(json_data)
                    }

            # ------------------------------------------------
            # Create hash
            # ------------------------------------------------

            event_hash = create_hash(

                video_name,

                event_type,

                event_data

            )

            # ------------------------------------------------
            # Check whether another record already
            # has this hash
            # ------------------------------------------------

            duplicate = connection.execute(

                text(
                    """
                    SELECT id
                    FROM detection_events
                    WHERE event_hash = :event_hash
                    LIMIT 1
                    """
                ),

                {
                    "event_hash":
                        event_hash
                }

            ).fetchone()

            # ------------------------------------------------
            # Existing duplicate hash
            #
            # This can happen if old data contains
            # exact duplicate events.
            #
            # We preserve the old records and make
            # their hashes unique by adding the ID.
            # ------------------------------------------------

            if duplicate:

                event_hash = create_hash(

                    video_name,

                    event_type,

                    {
                        "original_data":
                            event_data,

                        "legacy_record_id":
                            record_id

                    }

                )

            # ------------------------------------------------
            # Update record
            # ------------------------------------------------

            connection.execute(

                text(
                    """
                    UPDATE detection_events
                    SET event_hash = :event_hash
                    WHERE id = :record_id
                    """
                ),

                {
                    "event_hash":
                        event_hash,

                    "record_id":
                        record_id
                }

            )

            processed += 1

            if processed % 100 == 0:

                print(
                    f"Processed: {processed}"
                )

    print()
    print("=" * 70)
    print("EVENT HASH MIGRATION COMPLETED")
    print("=" * 70)

    print(
        f"Total processed: {processed}"
    )

    print("=" * 70)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    populate_event_hashes()