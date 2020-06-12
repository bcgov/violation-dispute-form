from django.db import models


class PreparedPdf(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)

    data = models.BinaryField()
