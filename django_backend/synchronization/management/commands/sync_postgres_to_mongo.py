from django.core.management.base import BaseCommand

from synchronization.services import synchronize_pending_records


class Command(BaseCommand):
    help = (
        "Synchronize pending PostgreSQL detection records "
        "to MongoDB."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            "Starting PostgreSQL to MongoDB synchronization..."
        )

        try:
            result = synchronize_pending_records()

            self.stdout.write("")
            self.stdout.write("Synchronization completed.")
            self.stdout.write(
                f"Total pending records : {result['total_pending']}"
            )
            self.stdout.write(
                f"Successfully synced   : {result['synced']}"
            )
            self.stdout.write(
                f"Already synced        : {result['already_synced']}"
            )
            self.stdout.write(
                f"Failed                : {result['failed']}"
            )

            if result["failed"] == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        "PostgreSQL to MongoDB synchronization "
                        "completed successfully."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Synchronization completed with some failures."
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Synchronization failed: {e}"
                )
            )