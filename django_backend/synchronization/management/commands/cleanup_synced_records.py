from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import connection

from mongodb_api.mongo import detection_events_collection


class Command(BaseCommand):
    help = (
        "Delete PostgreSQL detection records that were successfully "
        "synchronized to MongoDB more than 2 hours ago."
    )

    def handle(self, *args, **options):
        cutoff_time = datetime.utcnow() - timedelta(hours=2)

        self.stdout.write(
            f"Cleanup cutoff time: {cutoff_time}"
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM detection_events
                WHERE sync_status = %s
                  AND synced_at IS NOT NULL
                  AND synced_at <= %s
                ORDER BY id
                """,
                ["SYNCED", cutoff_time],
            )

            records = cursor.fetchall()

        total = len(records)

        self.stdout.write(
            f"Eligible records for deletion: {total}"
        )

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No PostgreSQL records are eligible for cleanup."
                )
            )
            return

        deleted = 0
        skipped = 0

        for record in records:
            postgres_id = record[0]

            # Safety check:
            # PostgreSQL can only be deleted if the corresponding
            # MongoDB document still exists.
            mongo_document = detection_events_collection.find_one(
                {"postgres_id": postgres_id}
            )

            if mongo_document is None:
                skipped += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping PostgreSQL ID {postgres_id}: "
                        "MongoDB document not found."
                    )
                )

                continue

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM detection_events
                    WHERE id = %s
                      AND sync_status = %s
                      AND synced_at IS NOT NULL
                      AND synced_at <= %s
                    """,
                    [
                        postgres_id,
                        "SYNCED",
                        cutoff_time,
                    ],
                )

                deleted += cursor.rowcount

        self.stdout.write(
            self.style.SUCCESS(
                f"Cleanup completed successfully. "
                f"Deleted records: {deleted}"
            )
        )

        if skipped > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Records skipped because MongoDB copies "
                    f"were not found: {skipped}"
                )
            )