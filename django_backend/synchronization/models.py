from django.db import models


class DetectionEvent(models.Model):
    """
    Django representation of the existing PostgreSQL
    detection_events table.

    IMPORTANT:
    managed = False means Django will NOT create,
    modify, or delete this PostgreSQL table.
    """

    id = models.IntegerField(primary_key=True)

    video_name = models.CharField(
        max_length=255
    )

    event_type = models.CharField(
        max_length=100
    )

    class_name = models.CharField(
        max_length=100
    )

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4
    )

    timestamp = models.DateTimeField()

    frame_number = models.IntegerField(
        null=True,
        blank=True
    )

    json_data = models.JSONField()

    created_at = models.DateTimeField()

    sync_status = models.CharField(
        max_length=20
    )

    synced_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        managed = False

        db_table = "detection_events"

        app_label = "synchronization"