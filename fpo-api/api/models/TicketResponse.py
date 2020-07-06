import uuid
from django.db import models



class TicketResponse(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    emailed_date = models.DateTimeField(blank=True, null=True)

    # stored encrypted when key_id is set
    result = models.BinaryField(blank=True, null=True)

    # encryption key identifier
    key_id = models.CharField(max_length=32, blank=True, null=True)

    # used by clients to open generated files
    file_guid = models.UUIDField(default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    hearing_attendance = models.CharField(max_length=255, blank=True, null=True)
    hearing_location = models.ForeignKey(
        "Location",
        related_name="location_ticket",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    ticket_number = models.CharField(max_length=255, blank=True, null=True)
    ticket_date = models.DateField(blank=True, null=True)
    deadline_date = models.DateField(blank=True, null=True)
    dispute_type = models.CharField(max_length=255, blank=True, null=True)

    pdf_filename = models.CharField(max_length=255, blank=True, null=True)

    printed_by = models.ForeignKey(
        "User",
        related_name="user_ticket_printed",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    printed_date = models.DateTimeField(blank=True, null=True)

    archived_by = models.ForeignKey(
        "User",
        related_name="user_ticket_archived",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    archived_date = models.DateTimeField(blank=True, null=True)

    prepared_pdf = models.ForeignKey(
        "PreparedPdf",
        related_name="pdf_ticket",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
