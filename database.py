from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/deepstream_db"


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
# UPDATE EXISTING DETECTION TABLE
# =========================================================

def update_detection_events_schema():

    try:

        with engine.begin() as connection:

            # -------------------------------------------------
            # Add sync_status if it does not exist
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
            # Add synced_at if it does not exist
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
            # Set existing NULL sync_status records to PENDING
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
            # Set NOT NULL constraint
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
            # Set default value
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
            # Create index for synchronization queries
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
            "Detection events synchronization schema "
            "updated successfully!"
        )

    except Exception as e:

        print(
            "Failed to update detection events schema:"
        )

        print(e)


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

except Exception as e:

    print(
        "Database connection failed:"
    )

    print(e)