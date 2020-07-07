from django.db import models


class PreparedPdf(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)

    # stored encrypted when key_id is set
    data = models.BinaryField()

    # encryption key identifier
    key_id = models.CharField(max_length=32, blank=True, null=True)
