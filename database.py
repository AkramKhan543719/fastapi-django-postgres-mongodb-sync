from sqlalchemy import (
    create_engine,
    text
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5432/"
    "deepstream_db"
)


# =========================================================
# DATABASE ENGINE
# =========================================================

engine = create_engine(
    DATABASE_URL,
    echo=False
)


# =========================================================
# DATABASE SESSION
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================================================
# SQLALCHEMY BASE
# =========================================================

Base = declarative_base()


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# UPDATE DETECTION EVENTS SCHEMA
# =========================================================

def update_detection_events_schema():

    try:

        with engine.begin() as connection:

            # -------------------------------------------------
            # sync_status
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    ALTER TABLE detection_events
                    ADD COLUMN IF NOT EXISTS
                    sync_status VARCHAR(20)
                    """
                )
            )

            # -------------------------------------------------
            # synced_at
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    ALTER TABLE detection_events
                    ADD COLUMN IF NOT EXISTS
                    synced_at TIMESTAMP
                    """
                )
            )

            # -------------------------------------------------
            # event_hash
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    ALTER TABLE detection_events
                    ADD COLUMN IF NOT EXISTS
                    event_hash VARCHAR(64)
                    """
                )
            )

            # -------------------------------------------------
            # Existing NULL sync status
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    UPDATE detection_events
                    SET sync_status = 'PENDING'
                    WHERE sync_status IS NULL
                    """
                )
            )

            # -------------------------------------------------
            # Existing NULL event hashes
            #
            # IMPORTANT:
            # Existing old records are given a unique
            # temporary hash.
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    UPDATE detection_events
                    SET event_hash =
                        md5(
                            COALESCE(id::text, '')
                            || '|'
                            || COALESCE(video_name, '')
                            || '|'
                            || COALESCE(event_type, '')
                        )
                    WHERE event_hash IS NULL
                    """
                )
            )

            # -------------------------------------------------
            # NOT NULL sync_status
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    ALTER TABLE detection_events
                    ALTER COLUMN sync_status
                    SET NOT NULL
                    """
                )
            )

            # -------------------------------------------------
            # DEFAULT sync_status
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    ALTER TABLE detection_events
                    ALTER COLUMN sync_status
                    SET DEFAULT 'PENDING'
                    """
                )
            )

            # -------------------------------------------------
            # NOT NULL event_hash
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    ALTER TABLE detection_events
                    ALTER COLUMN event_hash
                    SET NOT NULL
                    """
                )
            )

            # -------------------------------------------------
            # UNIQUE event_hash
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS
                    ux_detection_events_event_hash
                    ON detection_events(event_hash)
                    """
                )
            )

            # -------------------------------------------------
            # sync_status index
            # -------------------------------------------------

            connection.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS
                    ix_detection_events_sync_status
                    ON detection_events(sync_status)
                    """
                )
            )

        print(
            "Detection events schema updated successfully!"
        )

    except Exception as error:

        print(
            "Failed to update detection events schema:"
        )

        print(error)


# =========================================================
# TEST DATABASE CONNECTION
# =========================================================

try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

        print(
            "DeepStream PostgreSQL database "
            "connected successfully!"
        )

        print(
            "Database test result:",
            result.fetchone()
        )

except Exception as error:

    print(
        "Database connection failed:"
    )

    print(error)